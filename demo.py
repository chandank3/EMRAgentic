"""Example usage and demo script for Healthcare Care Coordinator Agent"""
import sys
sys.path.insert(0, '/Users/aavyaparnika/DorDevlopment/EMRAgentic')

from datetime import datetime, timedelta
from src.database import SessionLocal
from src.models.models import User, UserRole, Appointment, CarePlan, Medication, Document
from src.security.rbac import RBACManager, Permission
from src.security.pii_masking import PIIMasker, MaskingStrategy
from src.policy.policy_engine import PolicyEngine
from src.memory.memory import AgentMemory
from src.workflows.approval import ApprovalWorkflow
from src.tools.tools import TOOL_REGISTRY
import uuid


def demo_rbac():
    """Demonstrate RBAC functionality"""
    print("\n" + "="*60)
    print("RBAC DEMONSTRATION")
    print("="*60)
    
    # Check permissions for different roles
    roles = [UserRole.ADMIN, UserRole.CARE_COORDINATOR, UserRole.PATIENT, UserRole.PHYSICIAN]
    
    for role in roles:
        print(f"\n{role.value.upper()}:")
        permissions = RBACManager.get_role_permissions(role)
        print(f"  Total Permissions: {len(permissions)}")
        print(f"  Can approve care plans: {RBACManager.has_permission(role, Permission.APPROVE_CARE_PLAN)}")
        print(f"  Can create care plans: {RBACManager.has_permission(role, Permission.CREATE_CARE_PLAN)}")
        print(f"  Can manage users: {RBACManager.has_permission(role, Permission.MANAGE_USERS)}")


def demo_pii_masking():
    """Demonstrate PII masking functionality"""
    print("\n" + "="*60)
    print("PII MASKING DEMONSTRATION")
    print("="*60)
    
    sample_data = {
        "name": "John Doe",
        "ssn": "123-45-6789",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "address": "123 Main Street, Springfield",
        "dob": "01/15/1985",
        "mrn": "MRN: 987654321"
    }
    
    print("\nOriginal Data:")
    for key, value in sample_data.items():
        print(f"  {key}: {value}")
    
    print("\n\nPartial Masking:")
    masked_partial = PIIMasker.mask_dict(sample_data, MaskingStrategy.PARTIAL)
    for key, value in masked_partial.items():
        print(f"  {key}: {value}")
    
    print("\n\nFull Masking:")
    masked_full = PIIMasker.mask_dict(sample_data, MaskingStrategy.FULL)
    for key, value in masked_full.items():
        print(f"  {key}: {value}")


def demo_policy_engine():
    """Demonstrate policy engine functionality"""
    print("\n" + "="*60)
    print("POLICY ENGINE DEMONSTRATION")
    print("="*60)
    
    policy_engine = PolicyEngine()
    
    # Test valid care plan
    valid_plan = {
        "title": "Diabetes Management",
        "goals": ["Reduce A1C", "Improve diet"],
        "coordinator_id": str(uuid.uuid4()),
        "interventions": ["Monthly checkups", "Nutrition counseling"]
    }
    
    print("\nValidating VALID Care Plan:")
    result = policy_engine.validate_care_plan(valid_plan)
    print(f"  Valid: {result['valid']}")
    print(f"  Passed Rules: {result['passed_rules']}")
    print(f"  Violations: {len(result['violations'])}")
    
    # Test invalid care plan
    invalid_plan = {
        "title": "Incomplete Plan",
        "goals": [],  # No goals - violation
        "coordinator_id": None  # No coordinator - violation
    }
    
    print("\nValidating INVALID Care Plan:")
    result = policy_engine.validate_care_plan(invalid_plan)
    print(f"  Valid: {result['valid']}")
    print(f"  Violations: {len(result['violations'])}")
    for v in result['violations']:
        print(f"    - {v['message']} (Severity: {v['severity']})")
    
    # Get policy summary
    print("\nPolicy Summary:")
    summary = policy_engine.get_violations_report()
    print(f"  Total Rules: {summary['total_rules']}")
    print(f"  Enabled Rules: {summary['enabled_rules']}")
    print(f"  Rules by Type: {summary['rules_by_type']}")
    print(f"  Critical Rules: {len(summary['critical_rules'])}")


def demo_memory_management():
    """Demonstrate agent memory functionality"""
    print("\n" + "="*60)
    print("MEMORY MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    memory = AgentMemory()
    patient_id = str(uuid.uuid4())
    
    # Store some interactions
    print(f"\nStoring interactions for patient {patient_id[:8]}...")
    
    for i in range(5):
        memory.store_interaction(
            interaction_id=f"int-{i}",
            agent_name="CareCoordinator",
            action_type="appointment",
            patient_id=patient_id,
            content=f"Interaction {i+1}",
            metadata={"priority": "high" if i % 2 == 0 else "normal"},
            outcome="success"
        )
    
    # Retrieve patient history
    history = memory.get_patient_history(patient_id)
    print(f"\nRetrieved {len(history)} interactions for patient")
    print(f"  Most recent: {history[0]['timestamp']}")
    
    # Update patient context
    memory.update_patient_context(patient_id, {
        "last_visit": datetime.utcnow().isoformat(),
        "risk_level": "high"
    })
    
    # Get agent context
    context = memory.get_agent_context(patient_id, "CareCoordinator")
    print(f"\nAgent Context:")
    print(f"  Agent: {context['agent_name']}")
    print(f"  Recent Interactions: {len(context['recent_interactions'])}")
    print(f"  Context Data: {context['context']}")


def demo_tools():
    """Demonstrate tool registry"""
    print("\n" + "="*60)
    print("TOOL REGISTRY DEMONSTRATION")
    print("="*60)
    
    print("\nAvailable Tools:")
    for tool_name, tool in TOOL_REGISTRY.items():
        print(f"  - {tool.name}: {tool.description}")


def demo_approval_workflow():
    """Demonstrate approval workflow"""
    print("\n" + "="*60)
    print("APPROVAL WORKFLOW DEMONSTRATION")
    print("="*60)
    
    db = SessionLocal()
    workflow = ApprovalWorkflow(timeout_minutes=60)
    
    try:
        # Create a test care plan
        from src.models.models import CarePlan
        care_plan = CarePlan(
            patient_id=str(uuid.uuid4()),
            coordinator_id=str(uuid.uuid4()),
            title="Test Care Plan",
            description="For demonstration",
            goals=["Goal 1", "Goal 2"],
            interventions=["Intervention 1"]
        )
        db.add(care_plan)
        db.commit()
        db.refresh(care_plan)
        
        print(f"\nCreated test care plan: {care_plan.id}")
        
        # Create approval request
        request_data = {
            "care_plan_id": str(care_plan.id),
            "title": care_plan.title,
            "interventions": care_plan.interventions
        }
        
        approval_result = workflow.create_approval_request(str(care_plan.id), request_data, db)
        print(f"\nApproval Request Created:")
        print(f"  Status: {approval_result['status']}")
        print(f"  Expires At: {approval_result['expires_at']}")
        
        # Get pending requests
        pending = workflow.get_pending_requests(db)
        print(f"\nPending Requests: {len(pending)}")
        if pending:
            req = pending[0]
            print(f"  Care Plan: {req['care_plan_id'][:8]}...")
            print(f"  Requested At: {req['requested_at']}")
        
    except Exception as e:
        print(f"Error in approval workflow demo: {str(e)}")
    finally:
        db.close()


def demo_database_models():
    """Demonstrate database models"""
    print("\n" + "="*60)
    print("DATABASE MODELS DEMONSTRATION")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Create sample user
        user = User(
            email=f"coordinator_{uuid.uuid4()}@healthcare.local",
            username=f"coord_{uuid.uuid4()}",
            full_name="Jane Coordinator",
            role=UserRole.CARE_COORDINATOR,
            phone="555-1234",
            department="Cardiology"
        )
        # Note: In production, password should be hashed
        user.hashed_password = "hashed_password_here"
        
        print(f"\nCreated User Model:")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role.value}")
        print(f"  Department: {user.department}")
        
        # Show model structure
        print(f"\nKey Database Tables:")
        print(f"  - User (with RBAC roles)")
        print(f"  - Appointment (with status tracking)")
        print(f"  - CarePlan (with approval workflow)")
        print(f"  - Medication (with reminders)")
        print(f"  - Document (with vector indexing)")
        print(f"  - ApprovalRequest (for human-in-the-loop)")
        print(f"  - AuditLog (for compliance)")
        print(f"  - PolicyViolation (for governance)")
        
    finally:
        db.close()


def run_all_demos():
    """Run all demonstrations"""
    print("\n" + "#"*60)
    print("# HEALTHCARE CARE COORDINATOR AGENT - DEMO")
    print("#"*60)
    
    try:
        demo_rbac()
        demo_pii_masking()
        demo_policy_engine()
        demo_memory_management()
        demo_tools()
        demo_approval_workflow()
        demo_database_models()
        
        print("\n" + "#"*60)
        print("# DEMO COMPLETE")
        print("#"*60)
        print("\nNext steps:")
        print("1. Start the application: uvicorn src.main:app --reload")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Review README.md for detailed documentation")
        print("\n")
        
    except Exception as e:
        print(f"\nError running demos: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()
