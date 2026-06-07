# Architecture & Design Decisions

## System Architecture Overview

The Healthcare Care Coordinator Agent follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    REST API Layer                        │
│           (FastAPI with OpenAPI Documentation)          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Agent Orchestration Layer                   │
│  (AutoGen-based multi-agent coordination & workflows)   │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌─────────────────────────────────────────────────────────┐
│  Tool Registry | Memory Management | Policy Engine      │
│  (Structured   │ (Conversation    │ (Policy           │
│   tool calling)│  History & Context) │  Validation)     │
└─────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│         Security & Compliance Layer                      │
│  (RBAC | PII Masking | Audit Logging | Policy Engine)  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│          Persistence Layer                               │
│  (PostgreSQL with pgvector | Audit Trail | Metadata)   │
└─────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Multi-Agent Orchestration Pattern

**Problem**: Complex healthcare workflows require specialized AI agents with different expertise.

**Solution**: AutoGen-based multi-agent system where:
- **Care Coordinator** agent orchestrates the workflow
- **Clinical Support** agent provides evidence-based recommendations
- **Document Analyzer** processes medical records
- **Policy Compliance** agent validates rules
- **Escalation Manager** handles human approval

**Benefits**:
- Clear separation of concerns
- Specialist agents make better decisions in their domain
- Easy to test and modify individual agents
- Scalable to add more specialized agents

### 2. Tool Registry Pattern

**Problem**: Agents need access to various capabilities (appointment scheduling, care plan creation, etc.)

**Solution**: Centralized tool registry with:
- Structured tool definitions
- Type-safe method signatures
- Consistent error handling
- Audit logging integration

**Benefits**:
- Agents call tools consistently
- New tools can be added without modifying agents
- Tools are testable in isolation
- Clear interface contracts

### 3. Human-in-the-Loop Pattern

**Problem**: AI agents shouldn't make critical healthcare decisions alone.

**Solution**: Approval workflow where:
- Agents can recommend care plan changes
- Critical actions require human approval
- Approval requests have timeouts
- All decisions are audited

**Benefits**:
- Maintains human oversight
- Safety and liability protection
- Configurable approval thresholds
- Decision traceability

### 4. Policy Engine Pattern

**Problem**: Organizations have complex compliance requirements and rules.

**Solution**: Configurable policy engine:
- Declarative policy rules
- Pre-action validation
- Policy violation tracking
- Severity-based enforcement

**Benefits**:
- Policies are centralized and consistent
- Easy to audit policy compliance
- Violations are tracked
- Rules can be updated without code changes

### 5. RBAC Pattern

**Problem**: Different users need different permissions.

**Solution**: Role-Based Access Control with:
- Predefined roles (Admin, Coordinator, Physician, etc.)
- Role-to-permission mappings
- Resource-level access control
- Consistent permission checking

**Benefits**:
- Simple role assignment
- Flexible permission model
- Audit-friendly (easy to trace who can do what)
- Easily extensible

### 6. PII Masking Pattern

**Problem**: Healthcare data contains sensitive information that shouldn't be logged/displayed.

**Solution**: Multi-strategy PII masking:
- Pattern-based detection (SSN, email, phone, etc.)
- Multiple masking strategies (partial, full, hash)
- Field-level and content-based masking
- Data classification levels

**Benefits**:
- Reduces data breach risk
- HIPAA compliance
- Flexible masking based on context
- Works with any data type

## Data Flow Examples

### Appointment Booking Flow

```
User Request
    │
    ├─ API Validation
    │   └─ Schema validation
    │
    ├─ RBAC Check
    │   └─ User can schedule appointments?
    │
    ├─ Policy Validation
    │   └─ Appointment meets business rules?
    │
    ├─ Agent Orchestration
    │   ├─ Care Coordinator checks patient history
    │   ├─ Policy Compliance validates against rules
    │   └─ Escalation Manager requests approval if needed
    │
    ├─ Database Persistence
    │   └─ Store appointment + relationships
    │
    └─ Audit Logging
        └─ Log action, user, timestamp, changes
```

### Care Plan Creation Flow

```
Clinical Data Request
    │
    ├─ RBAC Check
    │   └─ User can create care plans?
    │
    ├─ Agent Orchestration
    │   ├─ Clinical Support analyzes patient:
    │   │   ├─ Medical history
    │   │   ├─ Current medications
    │   │   ├─ Lab results
    │   │   └─ Risk factors
    │   │
    │   ├─ Generates evidence-based:
    │   │   ├─ Goals
    │   │   ├─ Interventions
    │   │   └─ Timeline
    │   │
    │   ├─ Care Coordinator compiles plan
    │   ├─ Policy Compliance validates
    │   │
    │   └─ Escalation Manager sends for approval
    │       ├─ Creates approval request
    │       ├─ Notifies approver
    │       └─ Waits for decision
    │
    ├─ After Approval
    │   ├─ Update care plan status
    │   ├─ Activate interventions
    │   └─ Schedule follow-ups
    │
    └─ Audit Logging
        └─ Log full decision chain
```

## Technology Choices & Rationale

### FastAPI
- **Why**: Type-safe, fast, built-in docs, async support
- **Alternative Considered**: Django REST - overkill for this use case
- **Trade-off**: Less batteries-included than Django, but simpler for this use case

### PostgreSQL
- **Why**: Robust, ACID compliance, pgvector extension for embeddings
- **Alternative Considered**: MongoDB - less suitable for relational healthcare data
- **Trade-off**: Need to manage schema, but get strong consistency

### AutoGen
- **Why**: Multi-agent orchestration, human-in-the-loop support, flexible
- **Alternative Considered**: LangChain Agents - more complex setup
- **Trade-off**: Newer framework, less mature but better aligned with multi-agent needs

### Ollama (Local LLM)
- **Why**: Privacy-preserving, no API costs, full control
- **Alternative Considered**: OpenAI API - but healthcare data shouldn't leave premises
- **Trade-off**: Limited model quality, but acceptable for demo/PoC

## Security Considerations

### Data Protection
- PII is masked in logs and search results
- Sensitive fields encrypted in transit
- Database audit logging for all modifications

### Access Control
- All endpoints require RBAC check
- Resource-level access verification (user can only access own data)
- Role-based tool access

### Compliance
- HIPAA-aligned audit logging
- Policy enforcement before actions
- Approval workflows for critical changes
- Violation tracking

## Extensibility Points

### Add New Agents
```python
self.agents["specialized"] = autogen.ConversableAgent(
    name="SpecializedAgent",
    system_message="...",
    llm_config=self.llm_config
)
```

### Add New Tools
```python
class NewTool(HealthcareTool):
    def operation(self, **kwargs) -> Dict:
        # Implementation
        pass

TOOL_REGISTRY["new"] = NewTool()
```

### Add New Policies
```python
policy_engine.add_rule(PolicyRule(
    rule_id="NEW001",
    name="Policy Name",
    rule_type="resource_type",
    condition="...",
    severity="high"
))
```

### Add New Roles
```python
class UserRole(str, Enum):
    # Add new role
    SPECIALIST = "specialist"

# Add permissions
RBACManager.ROLE_PERMISSIONS[UserRole.SPECIALIST] = {
    Permission.VIEW_APPOINTMENT,
    # ...
}
```

## Performance Considerations

### Database
- Indexes on frequently queried fields (patient_id, created_at)
- Connection pooling for concurrent requests
- Query optimization for common patterns

### API
- Async request handling
- Pagination for large result sets
- Response caching for static resources

### Agent Orchestration
- Tool caching to avoid redundant lookups
- Batch processing for multiple patients
- Memory pruning to limit context size

## Monitoring & Observability

### Logging
- Structured JSON logging
- Separate logs for different components
- Configurable log levels

### Metrics
- API response times
- Agent execution duration
- Policy violation rates
- Approval decision times

### Tracing
- Request tracing with correlation IDs
- Agent interaction tracing
- Database query tracing

## Future Enhancements

1. **Distributed Agents**: Scale agents across multiple services
2. **Real-time Notifications**: WebSocket support for approvals
3. **Advanced Analytics**: Dashboards for care plan outcomes
4. **ML Integration**: Learn from past decisions
5. **Multi-language**: Support for multiple languages
6. **Mobile App**: Native mobile client
7. **Integration APIs**: EHR system integration
8. **Advanced Policy Engine**: Temporal policies, event-driven rules
