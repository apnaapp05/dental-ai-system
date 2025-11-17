# agent_server.py
from fastapi import FastAPI
from models import AppointmentAgentInput, AppointmentAgentOutput
from orchestrator import AgentOrchestrator

# Initialize the FastAPI application
app = FastAPI(title="Appointment Agent API")

# Initialize the core orchestrator (The ReAct loop manager)
agent_core = AgentOrchestrator()

@app.post("/api/v1/appointment/process", response_model=AppointmentAgentOutput)
async def process_request(request: AppointmentAgentInput):
    """
    Handles the incoming request, triggers the ReAct orchestration, and returns 
    the structured JSON output. (Step 9 Endpoint)
    """
    # This calls the full ReAct loop defined in your notebook (Step 1.3/2.2 logic)
    result = agent_core.process_request(request)
    return result