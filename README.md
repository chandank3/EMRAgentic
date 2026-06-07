# Healthcare Care Coordinator Agent

A production-grade, multi-agent agentic AI system for healthcare coordination that demonstrates enterprise-level patterns in AI orchestration, including planning, tool calling, memory management, human-in-the-loop approval, and comprehensive guardrails.

## 🎯 Project Overview

This project showcases a sophisticated healthcare coordination system using:
- **AutoGen** for multi-agent orchestration
- **FastAPI** for REST API
- **PostgreSQL** for persistent data
- **pgvector** for document retrieval via semantic search
- **Local LLM** (Ollama) for privacy-compliant inference
- **Role-Based Access Control (RBAC)** for user authorization
- **PII Masking** for data privacy
- **Policy Engine** for organizational compliance
- **Human-in-the-Loop Approval** for critical decisions
- **Comprehensive Audit Logging** for compliance

## 📋 Features

### Core Capabilities

1. **Appointment Booking**
   - Schedule appointments with availability checking
   - Conflict detection and resolution
   - Appointment status tracking
   - Visit summary generation

2. **Care Plan Recommendation**
   - Evidence-based care plan generation
   - Multi-goal intervention planning
   - Human approval workflow
   - Status tracking and timeline management

3. **Medication Reminder**
   - Active medication tracking
   - Reminder scheduling
   - Adherence monitoring
   - Drug interaction checks

4. **Document Retrieval**
   - Medical document storage and indexing
   - Vector similarity search
   - Document type classification
   - PII protection

5. **Visit Summary Generation**
   - Automated clinical note generation
   - Key findings extraction
   - Follow-up recommendation
   - Escalation identification

6. **Escalation Workflow**
   - Risk-based escalation routing
   - Urgent case handling
   - Escalation history tracking
   - Resolution tracking

### Enterprise Guardrails

1. **RBAC (Role-Based Access Control)**
   - Admin, Care Coordinator, Physician, Nurse, Approver, Patient roles
   - Fine-grained permission management
   - Resource-level access control

2. **PII Masking**
   - Multi-strategy masking (partial, full, hash)
   - Pattern-based detection (SSN, credit card, email, phone, etc.)
   - Field-level and content-based masking
   - Data classification levels

3. **Human Approval for Care Plans**
   - Multi-step approval workflow
   - Timeout management
   - Decision tracking and audit
   - Role-based approvers

4. **Audit Logs**
   - Comprehensive action logging
   - User and resource tracking
   - Status and error recording
   - HIPAA-compliant retention

5. **Policy Engine**
   - Configurable organizational policies
   - Pre-action validation
   - Policy violation tracking
   - Severity-based enforcement

## 🏗️ Architecture

```
Healthcare Care Coordinator Agent
├── Agent Orchestration (AutoGen)
│   ├── Care Coordinator (Main)
│   ├── Clinical Decision Support
│   ├── Document Analyzer
│   ├── Policy Compliance
│   └── Escalation Manager
├── Tool Registry
│   ├── Appointment Tools
│   ├── Care Plan Tools
│   ├── Medication Tools
│   ├── Document Tools
│   └── Audit Tools
├── Security Layer
│   ├── RBAC Manager
│   ├── PII Masking
│   └── Access Control Lists
├── Persistence
│   ├── PostgreSQL Database
│   ├── pgvector for Embeddings
│   └── Document Storage
├── Memory Management
│   ├── Agent Memory
│   └── Conversation History
├── Policy Engine
│   └── Policy Validation
└── FastAPI REST API
    └── Endpoints for all features
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Docker (optional, for containerization)
- Ollama (for local LLM)

### Installation

1. **Clone and setup repository:**
   ```bash
   cd EMRAgentic
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and LLM configuration
   ```

3. **Initialize database:**
   ```bash
   python -c "from src.database import init_db; init_db()"
   ```

4. **Start Ollama** (in a separate terminal):
   ```bash
   ollama serve
   ```

5. **Run the application:**
   ```bash
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000/docs` (Swagger UI)

### Docker Setup

```bash
docker-compose up -d
```

This starts:
- FastAPI server on port 8000
- PostgreSQL on port 5432
- Ollama on port 11434

## 📚 API Endpoints

### Appointments
- `POST /api/appointments` - Book appointment
- `GET /api/appointments/{patient_id}` - Get patient appointments

### Care Plans
- `POST /api/care-plans` - Create care plan
- `GET /api/care-plans/{patient_id}` - Get patient care plans

### Medications
- `GET /api/medications/{patient_id}` - Get patient medications

### Documents
- `GET /api/documents/{patient_id}` - Get patient documents

### Approval Workflows
- `GET /api/approvals/pending` - Get pending approvals
- `POST /api/approvals/{request_id}/approve` - Approve request

### Audit & Compliance
- `GET /api/audit/logs` - Get audit logs
- `GET /api/policies` - Get policy status
- `GET /api/memory/patient/{patient_id}` - Get agent memory

## 🔒 Security Features

### RBAC Implementation

```python
from src.security.rbac import RBACManager, Permission

# Check permissions
RBACManager.check_permission(user.role, Permission.APPROVE_CARE_PLAN)

# Get role permissions
permissions = RBACManager.get_role_permissions(user.role)
```

### PII Masking

```python
from src.security.pii_masking import PIIMasker, MaskingStrategy

# Mask text
masked = PIIMasker.mask_pii(text, MaskingStrategy.PARTIAL)

# Mask dictionary
masked_data = PIIMasker.mask_dict(data, MaskingStrategy.FULL)

# Redact fields
redacted = PIIMasker.redact_sensitive_fields(data, ['ssn', 'dob'])
```

### Approval Workflow

```python
from src.workflows.approval import ApprovalWorkflow
from src.database import SessionLocal

workflow = ApprovalWorkflow(timeout_minutes=60)
db = SessionLocal()

# Create approval
request = workflow.create_approval_request(care_plan_id, plan_data, db)

# Approve
result = workflow.approve_request(request_id, approver_id, db, "Approved")

# Get pending
pending = workflow.get_pending_requests(db)
```

### Policy Engine

```python
from src.policy.policy_engine import PolicyEngine

policy_engine = PolicyEngine()

# Validate
validation = policy_engine.validate_care_plan(plan_data)
if not validation['valid']:
    raise Exception(f"Policy violations: {validation['violations']}")

# Get report
report = policy_engine.get_violations_report()
```

## 🧠 Agent Orchestration

The system uses AutoGen to coordinate multiple specialized agents:

1. **Care Coordinator** - Main orchestrator, manages workflows
2. **Clinical Decision Support** - Evidence-based recommendations
3. **Document Analyzer** - Medical document processing
4. **Policy Compliance** - Policy validation and enforcement
5. **Escalation Manager** - Escalation routing and approval

```python
from src.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Execute workflow
result = orchestrator.execute_workflow(
    "care_plan",
    {"patient_id": "...", "context": {...}}
)
```

## 💾 Memory Management

The system maintains two types of memory:

1. **Agent Memory** - Interaction history and patient context
2. **Conversation History** - Dialog between agents and humans

```python
from src.memory.memory import AgentMemory

memory = AgentMemory()

# Store interaction
memory.store_interaction(
    interaction_id="...",
    agent_name="CareCoordinator",
    action_type="appointment",
    patient_id="...",
    content="...",
    metadata={},
    outcome="..."
)

# Retrieve patient history
history = memory.get_patient_history("patient_id", limit=20)

# Get agent context
context = memory.get_agent_context("patient_id", "CareCoordinator")
```

## 🗄️ Database Schema

Key tables:
- **user** - User accounts and roles
- **appointment** - Appointment records
- **care_plan** - Care plans with goals and interventions
- **medication** - Patient medications
- **document** - Medical documents with metadata
- **approval_request** - Pending approvals
- **audit_log** - Complete action audit trail
- **policy_violation** - Tracked policy violations

## 📊 Example Workflows

### Appointment Booking Workflow
```
User Request
    ↓
Care Coordinator Agent
    ├→ Validate against policies
    ├→ Check provider availability
    ├→ Check patient constraints
    └→ Request human approval
         ↓
    Approval Manager → Human Review
         ↓
    Appointment Created
    ↓
Audit Log Entry
```

### Care Plan Creation Workflow
```
Clinical Data
    ↓
Clinical Decision Support
    ├→ Analyze patient history
    ├→ Recommend evidence-based interventions
    └→ Flag drug interactions
         ↓
Care Coordinator
    ├→ Compile comprehensive plan
    ├→ Set goals and timeline
    └→ Assign to coordinator
         ↓
Policy Compliance
    ├→ Validate against policies
    └→ Check permissions
         ↓
Escalation Manager → Human Approval
         ↓
Care Plan Approved & Activated
    ↓
Audit Log Entry
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📈 Monitoring & Logging

Application logs are written to stdout with structured JSON format. Key metrics:
- API response times
- Agent execution times
- Policy violations
- Approval decision times
- Error rates

View logs:
```bash
tail -f application.log
```

## 🎓 Interview Topics Demonstrated

This project demonstrates practical knowledge of:

1. **Agent Orchestration** - Multi-agent workflows with dependencies
2. **Tool Calling** - Structured tool definitions and execution
3. **Planning** - Complex workflow planning and execution
4. **Memory Management** - Conversation history and context
5. **Human-in-the-Loop** - Approval workflows with timeouts
6. **RBAC** - Role-based access control implementation
7. **Data Privacy** - PII masking and data classification
8. **Policy Engine** - Configurable compliance validation
9. **Audit Logging** - Comprehensive action tracking
10. **Error Handling** - Resilient error management
11. **Database Design** - Normalized schemas with relationships
12. **API Design** - RESTful API with proper validation

## 🔧 Configuration

Key configuration options in `.env`:

- `DATABASE_URL` - PostgreSQL connection
- `OLLAMA_MODEL` - LLM model name
- `ENABLE_PII_MASKING` - PII masking on/off
- `REQUIRE_HUMAN_APPROVAL_FOR_CARE_PLANS` - Mandatory approval
- `AUDIT_LOG_RETENTION_DAYS` - Retention policy
- `POLICY_VALIDATION_ENABLED` - Policy enforcement

## 📝 License

MIT

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first.

## 📧 Support

For questions or issues, reach out to the project maintainers.

---

Built with ❤️ for healthcare coordination and agentic AI interviews.
