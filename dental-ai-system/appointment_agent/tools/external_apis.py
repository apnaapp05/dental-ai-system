# appointment_agent/tools/external_apis.py
from typing import Optional, Dict, Any

class MockAPITools:
    """
    Simulates the backend Dental Management System (DMS) API calls.
    In production, these would be HTTP requests to your actual API endpoints.
    """
    
    def search_availability(self, procedure_type: str, requested_datetime_range: str, doctor_name: Optional[str] = None) -> Dict[str, Any]:
        """Tool 1: Searches for available appointment slots."""
        print(f"DEBUG: Mock Tool: Searching for {procedure_type} on {requested_datetime_range}...")
        # Simulate a successful return for the test case
        if "next Tuesday" in requested_datetime_range:
            return {"status": "success", "available_slots": [{"slot_id": "SLOT-123", "time": "2025-11-25T15:00:00", "doctor": "Dr. Jones"}]}
        return {"status": "unavailable", "message": "No slots found. Agent should ask for alternatives."}
        
    def schedule_appointment(self, patient_id: str, slot_id: str, procedure_type: str) -> Dict[str, Any]:
        """Tool 2: Books a final appointment slot."""
        print(f"DEBUG: Mock Tool: Scheduling {procedure_type} for {patient_id} at slot {slot_id}...")
        if "SLOT-123" in slot_id:
            return {"status": "success", "confirmation_id": "CONF-9876", "details": "Cleaning confirmed with Dr. Jones."}
        return {"status": "error", "message": "Slot taken during booking attempt."}

    # Implement manage_appointment and send_reminder tools here
    def manage_appointment(self, patient_id: str, action: str, new_slot_id: Optional[str] = None):
        if action == "cancel":
            return {"status": "success", "message": f"Appointment for {patient_id} cancelled."}
        return {"status": "error", "message": "Management tool failed."}

    def send_reminder(self, patient_id: str, appointment_id: str, message_type: str):
        return {"status": "success", "message": f"Reminder sent via {message_type}."}

TOOL_MANAGER = MockAPITools()