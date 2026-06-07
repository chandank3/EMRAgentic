"""Tool definitions for agent use"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from src.database import SessionLocal
from src.models.models import (
    Appointment, CarePlan, Medication, Document, AuditLog,
    AppointmentStatus, CarePlanStatus, AuditAction
)
import logging

logger = logging.getLogger(__name__)


class HealthcareTool:
    """Base tool class"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class AppointmentTool(HealthcareTool):
    """Appointment management tools"""

    def __init__(self):
        super().__init__(
            "AppointmentTool",
            "Schedule, reschedule, and manage patient appointments"
        )

    def schedule_appointment(self, patient_id: str, appointment_data: Dict) -> Dict:
        """Schedule a new appointment"""
        try:
            db = SessionLocal()
            appointment = Appointment(
                patient_id=patient_id,
                scheduled_by_id=appointment_data.get("coordinator_id"),
                title=appointment_data.get("title"),
                description=appointment_data.get("description"),
                appointment_type=appointment_data.get("type", "checkup"),
                scheduled_at=datetime.fromisoformat(appointment_data.get("scheduled_at")),
                duration_minutes=appointment_data.get("duration", 30),
                location=appointment_data.get("location"),
            )
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            logger.info(f"Appointment {appointment.id} scheduled for patient {patient_id}")
            return {"success": True, "appointment_id": str(appointment.id)}
        except Exception as e:
            logger.error(f"Error scheduling appointment: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_available_slots(self, provider_id: str, date: str) -> List[Dict]:
        """Get available appointment slots for a provider"""
        # Mock implementation - in production, integrate with scheduling system
        available_slots = [
            {"time": "09:00", "duration": 30, "available": True},
            {"time": "10:00", "duration": 30, "available": True},
            {"time": "14:00", "duration": 30, "available": False},
            {"time": "15:00", "duration": 30, "available": True},
        ]
        return available_slots

    def complete_appointment(self, appointment_id: str, summary: str, notes: str) -> Dict:
        """Mark appointment as completed and store summary"""
        try:
            db = SessionLocal()
            appointment = db.query(Appointment).filter_by(id=appointment_id).first()
            if not appointment:
                return {"success": False, "error": "Appointment not found"}
            
            appointment.status = AppointmentStatus.COMPLETED
            appointment.summary = summary
            appointment.notes = notes
            db.commit()
            logger.info(f"Appointment {appointment_id} marked as completed")
            return {"success": True, "appointment_id": appointment_id}
        except Exception as e:
            logger.error(f"Error completing appointment: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()


class CarePlanTool(HealthcareTool):
    """Care plan management tools"""

    def __init__(self):
        super().__init__(
            "CarePlanTool",
            "Create, update, and manage patient care plans"
        )

    def create_care_plan(self, patient_id: str, plan_data: Dict) -> Dict:
        """Create a new care plan"""
        try:
            db = SessionLocal()
            care_plan = CarePlan(
                patient_id=patient_id,
                coordinator_id=plan_data.get("coordinator_id"),
                title=plan_data.get("title"),
                description=plan_data.get("description"),
                goals=plan_data.get("goals", []),
                interventions=plan_data.get("interventions", []),
                timeline=plan_data.get("timeline"),
            )
            db.add(care_plan)
            db.commit()
            db.refresh(care_plan)
            logger.info(f"Care plan {care_plan.id} created for patient {patient_id}")
            return {"success": True, "care_plan_id": str(care_plan.id)}
        except Exception as e:
            logger.error(f"Error creating care plan: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def submit_for_approval(self, care_plan_id: str, approver_id: str) -> Dict:
        """Submit care plan for human approval"""
        try:
            db = SessionLocal()
            care_plan = db.query(CarePlan).filter_by(id=care_plan_id).first()
            if not care_plan:
                return {"success": False, "error": "Care plan not found"}
            
            care_plan.status = CarePlanStatus.PENDING_APPROVAL
            db.commit()
            logger.info(f"Care plan {care_plan_id} submitted for approval")
            return {"success": True, "care_plan_id": care_plan_id, "status": "pending_approval"}
        except Exception as e:
            logger.error(f"Error submitting for approval: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()


class MedicationTool(HealthcareTool):
    """Medication management tools"""

    def __init__(self):
        super().__init__(
            "MedicationTool",
            "Manage medication reminders and adherence tracking"
        )

    def add_medication(self, patient_id: str, medication_data: Dict) -> Dict:
        """Add new medication to patient's medication list"""
        try:
            db = SessionLocal()
            medication = Medication(
                patient_id=patient_id,
                name=medication_data.get("name"),
                dosage=medication_data.get("dosage"),
                frequency=medication_data.get("frequency"),
                route=medication_data.get("route"),
                start_date=datetime.fromisoformat(medication_data.get("start_date")),
                end_date=datetime.fromisoformat(medication_data.get("end_date")) if medication_data.get("end_date") else None,
                instructions=medication_data.get("instructions"),
                side_effects=medication_data.get("side_effects"),
            )
            db.add(medication)
            db.commit()
            db.refresh(medication)
            logger.info(f"Medication {medication.id} added for patient {patient_id}")
            return {"success": True, "medication_id": str(medication.id)}
        except Exception as e:
            logger.error(f"Error adding medication: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_medication_reminders(self, patient_id: str) -> List[Dict]:
        """Get active medications requiring reminders"""
        try:
            db = SessionLocal()
            medications = db.query(Medication).filter(
                Medication.patient_id == patient_id,
                Medication.is_active == True,
                Medication.start_date <= datetime.utcnow(),
                (Medication.end_date.is_(None) | (Medication.end_date >= datetime.utcnow()))
            ).all()
            
            reminders = [
                {
                    "medication_id": str(m.id),
                    "name": m.name,
                    "dosage": m.dosage,
                    "frequency": m.frequency,
                    "next_reminder": self._calculate_next_reminder(m)
                }
                for m in medications
            ]
            return reminders
        except Exception as e:
            logger.error(f"Error retrieving medication reminders: {str(e)}")
            return []
        finally:
            db.close()

    def _calculate_next_reminder(self, medication: Medication) -> str:
        """Calculate next reminder time based on frequency"""
        # Simplified calculation - in production, use more sophisticated scheduling
        frequency_map = {
            "once daily": timedelta(days=1),
            "twice daily": timedelta(hours=12),
            "every 8 hours": timedelta(hours=8),
            "as needed": None,
        }
        interval = frequency_map.get(medication.frequency, timedelta(hours=12))
        if interval:
            return (datetime.utcnow() + interval).isoformat()
        return "as needed"


class DocumentTool(HealthcareTool):
    """Document retrieval and analysis tools"""

    def __init__(self):
        super().__init__(
            "DocumentTool",
            "Store, retrieve, and analyze medical documents with vector search"
        )

    def retrieve_patient_documents(self, patient_id: str, doc_type: Optional[str] = None) -> List[Dict]:
        """Retrieve patient's documents"""
        try:
            db = SessionLocal()
            query = db.query(Document).filter_by(patient_id=patient_id)
            if doc_type:
                query = query.filter_by(document_type=doc_type)
            
            documents = query.all()
            result = [
                {
                    "document_id": str(d.id),
                    "filename": d.filename,
                    "type": d.document_type,
                    "created_at": d.created_at.isoformat(),
                    "description": d.description,
                }
                for d in documents
            ]
            return result
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
        finally:
            db.close()

    def search_documents(self, patient_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Search documents using vector similarity"""
        # In production, integrate with pgvector or Milvus
        logger.info(f"Searching documents for patient {patient_id} with query: {query}")
        return [
            {
                "document_id": "doc123",
                "similarity_score": 0.92,
                "filename": "lab_results_2024.pdf",
                "excerpt": "Relevant excerpt from document..."
            }
        ]


class AuditTool(HealthcareTool):
    """Audit logging tools"""

    def __init__(self):
        super().__init__(
            "AuditTool",
            "Log all system actions for compliance and audit purposes"
        )

    def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None,
        status: str = "success"
    ) -> Dict:
        """Log an action to audit trail"""
        try:
            db = SessionLocal()
            audit_log = AuditLog(
                user_id=user_id,
                action=AuditAction[action.upper()],
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                status=status,
            )
            db.add(audit_log)
            db.commit()
            logger.info(f"Audit log created: {action} on {resource_type} {resource_id}")
            return {"success": True, "log_id": str(audit_log.id)}
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()


# Tool registry
TOOL_REGISTRY = {
    "appointment": AppointmentTool(),
    "care_plan": CarePlanTool(),
    "medication": MedicationTool(),
    "document": DocumentTool(),
    "audit": AuditTool(),
}
