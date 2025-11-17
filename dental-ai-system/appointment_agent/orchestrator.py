# appointment_agent/orchestrator.py
from models import (
    AppointmentAgentInput, AppointmentAgentOutput, ToolCall, 
    TOOL_FUNCTIONS_DECLARATION
)
from tools.external_apis import TOOL_MANAGER
import json
from typing import Dict, Any, Union

# --------------------------------------------------------------------------
# Conceptual LLM Interface (In production, replace with Google Gemini/Vertex SDK)
# --------------------------------------------------------------------------

def _get_system_prompt(input_data: AppointmentAgentInput) -> str:
    """Constructs the full system prompt (Step 3) including history and tool definitions."""
    # Step 3: System Instruction (Role, Constraints)
    system_instruction = """
    You are the Appointment Agent, a highly professional, polite, and efficient "Dental Clinic Booking Coordinator." 
    Your mission is to manage the end-to-end patient appointment lifecycle.
    ... [Core Constraints and Reflection rules from Step 3 go here] ...
    """
    # Tool definitions are passed via function calling mechanism of the LLM SDK, not in the prompt string.
    
    # Session History (Step 6) - formatted for in-context learning
    history_str = "\n".join([f"{turn.role}: {turn.content}" for turn in input_data.session_history])
    
    # Patient Context
    context_str = f"Patient ID: {input_data.patient_context.patient_id}, Name: {input_data.patient_context.name}"
    
    # Combined Prompt
    return f"{system_instruction}\n\n[CONTEXT]:\n{context_str}\n\n[HISTORY]:\n{history_str}"


def run_llm_step(prompt: str, tool_defs: List[Dict]) -> AppointmentAgentOutput:
    """
    Conceptual LLM call. In a real app, this uses the SDK (e.g., gemini.generate_content)
    to get a response that is either text or a structured function call.
    """
    # Placeholder: Using the simplified state-aware logic from our validation phase
    
    # 1. RAG/A2A Check (Co-Pay) - Final step in the ReAct loop
    if "The previous tool call to schedule_appointment returned" in prompt:
        print("MOCK LLM Thought: Booking successful. Generating final response with A2A route.")
        return AppointmentAgentOutput(
            final_response="Your cleaning appointment is confirmed. I am now routing your co-pay question to the Revenue Agent.",
            status="SUCCESS",
            next_agent_route="RevenueAgent/CoPayLookup"
        )
        
    # 2. Tool Follow-up (Schedule Appointment)
    elif "The previous tool call to search_availability returned" in prompt:
        print("MOCK LLM Thought: Availability confirmed. Proceeding to book appointment.")
        return AppointmentAgentOutput(
            final_response="Availability confirmed. Finalizing the booking now...",
            status="PENDING_TOOL_CALL",
            tool_call=ToolCall(
                function_name="schedule_appointment",
                arguments={"patient_id": "P-45890", "slot_id": "SLOT-123", "procedure_type": "cleaning"}
            )
        )
        
    # 3. Initial Request (Search Availability)
    elif "book a cleaning next Tuesday" in prompt:
        print("MOCK LLM Thought: Initial booking request. Must check availability first.")
        return AppointmentAgentOutput(
            final_response="One moment while I check availability...",
            status="PENDING_TOOL_CALL",
            tool_call=ToolCall(
                function_name="search_availability",
                arguments={"procedure_type": "cleaning", "requested_datetime_range": "next Tuesday at 3 PM", "doctor_name": "Dr. Jones"}
            )
        )
        
    # 4. Routing/Out of Scope
    elif "billing" in prompt.lower() or "copay" in prompt.lower():
        print("MOCK LLM Thought: Direct billing/co-pay query. Routing to Revenue Agent.")
        return AppointmentAgentOutput(
            final_response="I cannot directly handle billing. I will route your query to the Revenue Agent.",
            status="SUCCESS",
            next_agent_route="RevenueAgent/BillingInquiry"
        )

    return AppointmentAgentOutput(final_response="Please confirm your request.", status="CLARIFICATION_NEEDED")

# --------------------------------------------------------------------------
# Agent Orchestrator (ReAct Loop Implementation)
# --------------------------------------------------------------------------

class AgentOrchestrator:
    def __init__(self, max_steps: int = 5):
        self.max_steps = max_steps

    def process_request(self, input_data: AppointmentAgentInput) -> AppointmentAgentOutput:
        """Manages the ReAct Planning loop (Step 4)."""
        
        # 1. Construct the initial prompt using system instructions (Step 3)
        current_prompt = _get_system_prompt(input_data)
        current_prompt += f"\n\n[USER QUERY]: {input_data.user_query}"
        
        for step in range(self.max_steps):
            print(f"--- ReAct Step {step + 1} ---")
            
            # 2. Action: Call LLM (Thought & Action generation)
            agent_output: AppointmentAgentOutput = run_llm_step(current_prompt, TOOL_FUNCTIONS_DECLARATION)
            
            if agent_output.status not in ["PENDING_TOOL_CALL"]:
                # Success, Clarification, Error, or Route - loop terminates
                return agent_output
            
            # 3. Tool Execution is required
            if agent_output.tool_call:
                tool_call = agent_output.tool_call
                tool_func = getattr(TOOL_MANAGER, tool_call.function_name, None)
                
                if tool_func:
                    # Execute the tool using reflection to get the function from the manager
                    tool_result = tool_func(**tool_call.arguments)
                    
                    # 4. Observation: Prepare new prompt for the next LLM turn (Prompt Chaining)
                    # The tool result becomes the observation in the next prompt
                    observation_str = json.dumps(tool_result)
                    current_prompt = f"CONTINUE: The previous tool call to {tool_call.function_name} returned the following result: {observation_str}. Based on this, what is the next action (or final answer)?"
                else:
                    return AppointmentAgentOutput(final_response=f"Internal tool error: {tool_call.function_name} not found.", status="ERROR")
                    
        return AppointmentAgentOutput(final_response="Max planning steps reached without resolution.", status="ERROR")