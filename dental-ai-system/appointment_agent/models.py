# appointment_agent/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- Shared Components ---
class PatientContext(BaseModel):
    patient_id: str = Field(..., description="Unique identifier for the patient.")
    name: str
    preferred_contact: str = Field("sms", enum=["email", "sms", "phone"])

class SessionTurn(BaseModel):
    role: str = Field(..., enum=["user", "agent", "system"])
    content: str

class ToolCall(BaseModel):
    function_name: str
    arguments: Dict[str, Any]

# --- Input Schema (AppointmentAgentInput) ---
class AppointmentAgentInput(BaseModel):
    user_query: str = Field(..., description="The natural language request from the user.")
    patient_context: PatientContext
    session_history: List[SessionTurn] = []

# --- Output Schema (AppointmentAgentOutput) ---
class AppointmentAgentOutput(BaseModel):
    final_response: str = Field(..., description="The final natural language response to be shown to the user.")
    status: str = Field(..., enum=["SUCCESS", "PENDING_TOOL_CALL", "CLARIFICATION_NEEDED", "ERROR"])
    tool_call: Optional[ToolCall] = None
    next_agent_route: Optional[str] = None

# Tool Definitions for the LLM (Step 4 artifact)
TOOL_FUNCTIONS_DECLARATION = [
    {
        "name": "search_availability",
        "description": "Searches for available appointment slots.",
        "parameters": {
            "type": "object",
            "properties": {
                "procedure_type": {"type": "string"},
                "requested_datetime_range": {"type": "string"},
                "doctor_name": {"type": "string"}
            },
            "required": ["procedure_type", "requested_datetime_range"]
        }
    },
    {
        "name": "schedule_appointment",
        "description": "Books a final appointment slot.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "string"},
                "slot_id": {"type": "string"},
                "procedure_type": {"type": "string"}
            },
            "required": ["patient_id", "slot_id"]
        }
    },
    # ... (Add manage_appointment and send_reminder here as defined in Step 4)
]