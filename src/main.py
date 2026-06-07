"""Main FastAPI application"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import sys

from src.config import get_settings
from src.database import init_db, close_db, get_db
from src.models.models import Base
from src.agents.orchestrator import AgentOrchestrator
from src.memory.memory import AgentMemory, ConversationHistory
from src.policy.policy_engine import PolicyEngine
from src.security.rbac import RBACManager
from src.security.pii_masking import PIIMasker, MaskingStrategy
from src.tools.tools import TOOL_REGISTRY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

settings = get_settings()


# Global instances
agent_orchestrator: AgentOrchestrator = None
agent_memory: AgentMemory = None
conversation_history: ConversationHistory = None
policy_engine: PolicyEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting Healthcare Care Coordinator Agent...")
    
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed (API will run in degraded mode): {str(e)}")
        logger.info("Continuing startup without database...")
    
    global agent_orchestrator, agent_memory, conversation_history, policy_engine
    agent_orchestrator = AgentOrchestrator()
    agent_memory = AgentMemory()
    conversation_history = ConversationHistory()
    policy_engine = PolicyEngine()
    
    logger.info("Agent orchestration, memory, and policy engine initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Healthcare Care Coordinator Agent",
    description="Multi-agent agentic AI system for healthcare coordination",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Healthcare Care Coordinator Agent",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


# Appointment endpoints
@app.post("/api/appointments")
async def book_appointment(
    patient_id: str,
    appointment_data: dict,
    db=Depends(get_db)
):
    """Book a new appointment"""
    try:
        # Validate against policies
        validation = policy_engine.validate_appointment(appointment_data)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Policy violations: {validation['violations']}"
            )
        
        # Execute workflow
        result = agent_orchestrator.execute_workflow(
            "appointment_booking",
            {
                "patient_id": patient_id,
                "appointment_data": appointment_data
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error booking appointment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/appointments/{patient_id}")
async def get_appointments(patient_id: str, db=Depends(get_db)):
    """Get patient's appointments"""
    try:
        from src.models.models import Appointment
        appointments = db.query(Appointment).filter_by(patient_id=patient_id).all()
        return [
            {
                "id": str(a.id),
                "title": a.title,
                "type": a.appointment_type,
                "status": a.status,
                "scheduled_at": a.scheduled_at.isoformat(),
                "summary": a.summary
            }
            for a in appointments
        ]
    except Exception as e:
        logger.error(f"Error retrieving appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Care plan endpoints
@app.post("/api/care-plans")
async def create_care_plan(
    patient_id: str,
    plan_data: dict,
    db=Depends(get_db)
):
    """Create a new care plan"""
    try:
        # Validate against policies
        validation = policy_engine.validate_care_plan(plan_data)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Policy violations: {validation['violations']}"
            )
        
        # Execute workflow
        result = agent_orchestrator.execute_workflow(
            "care_plan",
            {
                "patient_id": patient_id,
                "context": plan_data
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error creating care plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/care-plans/{patient_id}")
async def get_care_plans(patient_id: str, db=Depends(get_db)):
    """Get patient's care plans"""
    try:
        from src.models.models import CarePlan
        plans = db.query(CarePlan).filter_by(patient_id=patient_id).all()
        return [
            {
                "id": str(p.id),
                "title": p.title,
                "status": p.status,
                "goals": p.goals,
                "interventions": p.interventions,
                "created_at": p.created_at.isoformat()
            }
            for p in plans
        ]
    except Exception as e:
        logger.error(f"Error retrieving care plans: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Medication endpoints
@app.get("/api/medications/{patient_id}")
async def get_medications(patient_id: str, db=Depends(get_db)):
    """Get patient's active medications"""
    try:
        from src.models.models import Medication
        from datetime import datetime
        
        medications = db.query(Medication).filter(
            Medication.patient_id == patient_id,
            Medication.is_active == True
        ).all()
        
        return [
            {
                "id": str(m.id),
                "name": m.name,
                "dosage": m.dosage,
                "frequency": m.frequency,
                "route": m.route,
                "instructions": m.instructions
            }
            for m in medications
        ]
    except Exception as e:
        logger.error(f"Error retrieving medications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Document endpoints
@app.get("/api/documents/{patient_id}")
async def get_documents(patient_id: str, db=Depends(get_db)):
    """Get patient's documents"""
    try:
        from src.models.models import Document
        documents = db.query(Document).filter_by(patient_id=patient_id).all()
        return [
            {
                "id": str(d.id),
                "filename": d.filename,
                "type": d.document_type,
                "created_at": d.created_at.isoformat(),
                "description": d.description
            }
            for d in documents
        ]
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Approval workflow endpoints
@app.get("/api/approvals/pending")
async def get_pending_approvals(db=Depends(get_db)):
    """Get pending approval requests"""
    try:
        from src.models.models import ApprovalRequest
        pending = db.query(ApprovalRequest).filter_by(status="pending").all()
        return [
            {
                "id": str(a.id),
                "care_plan_id": str(a.care_plan_id),
                "requested_at": a.requested_at.isoformat(),
                "request_data": a.request_data
            }
            for a in pending
        ]
    except Exception as e:
        logger.error(f"Error retrieving pending approvals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/approvals/{request_id}/approve")
async def approve_request(
    request_id: str,
    approver_id: str,
    reason: str = None,
    db=Depends(get_db)
):
    """Approve a care plan"""
    try:
        from src.workflows.approval import ApprovalWorkflow
        workflow = ApprovalWorkflow()
        result = workflow.approve_request(request_id, approver_id, db, reason)
        return result
    except Exception as e:
        logger.error(f"Error approving request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Memory and audit endpoints
@app.get("/api/audit/logs")
async def get_audit_logs(
    resource_type: str = None,
    limit: int = 100,
    db=Depends(get_db)
):
    """Get audit logs"""
    try:
        from src.models.models import AuditLog
        query = db.query(AuditLog)
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
        return [
            {
                "id": str(l.id),
                "action": l.action,
                "resource_type": l.resource_type,
                "resource_id": str(l.resource_id) if l.resource_id else None,
                "status": l.status,
                "created_at": l.created_at.isoformat(),
                "details": l.details
            }
            for l in logs
        ]
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Policy endpoints
@app.get("/api/policies")
async def get_policies():
    """Get all active policies"""
    try:
        return policy_engine.get_violations_report()
    except Exception as e:
        logger.error(f"Error retrieving policies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent memory endpoints
@app.get("/api/memory/patient/{patient_id}")
async def get_patient_memory(patient_id: str):
    """Get agent memory for patient"""
    try:
        return {
            "patient_id": patient_id,
            "history": agent_memory.get_patient_history(patient_id, limit=50)
        }
    except Exception as e:
        logger.error(f"Error retrieving patient memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
