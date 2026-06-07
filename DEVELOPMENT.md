# Healthcare Care Coordinator Agent - Development Setup

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Ollama
- Git

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repo-url>
cd EMRAgentic
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with local settings
```

### 5. Setup PostgreSQL

Create database:
```bash
createdb healthcare_coordinator
psql healthcare_coordinator < schema.sql  # If schema file exists
```

Or let SQLAlchemy create tables:
```bash
python -c "from src.database import init_db; init_db()"
```

### 6. Start Ollama

In a separate terminal:
```bash
ollama serve
ollama pull mistral  # Download the model
```

### 7. Run Application
```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Development Setup

### Quick Start with Docker Compose
```bash
docker-compose up -d
```

Wait for all services to be healthy:
```bash
docker-compose ps
```

Access the application at http://localhost:8000

### Clean Up
```bash
docker-compose down -v
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_security.py -v
```

### Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Database Migrations

Using Alembic for migrations:

```bash
# Generate migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Common Issues

### PostgreSQL Connection Error
- Check if PostgreSQL service is running
- Verify `DATABASE_URL` in `.env`
- Ensure database exists: `createdb healthcare_coordinator`

### Ollama Not Found
- Ensure Ollama is installed and running
- Check `OLLAMA_BASE_URL` in `.env`
- Pull required model: `ollama pull mistral`

### PII Masking Issues
- Check `ENABLE_PII_MASKING` setting in `.env`
- Verify PII patterns in `src/security/pii_masking.py`

## Performance Tuning

### PostgreSQL
- Increase `shared_buffers` for large datasets
- Add indexes on frequently queried columns
- Use connection pooling

### FastAPI
- Enable uvicorn workers: `--workers 4`
- Configure request timeouts
- Enable gzip compression

### Vector Search
- Monitor pgvector performance
- Consider indexing embeddings
- Batch similarity searches

## Monitoring & Logging

### View Logs
```bash
tail -f logs/application.log
```

### Debug Mode
Set `DEBUG=True` in `.env` for detailed logging

### Performance Metrics
```python
import time
start = time.time()
# ... operation ...
duration = time.time() - start
logger.info(f"Operation took {duration:.2f}s")
```

## API Examples

### Schedule Appointment
```bash
curl -X POST http://localhost:8000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "123",
    "title": "Checkup",
    "scheduled_at": "2024-12-15T10:00:00",
    "duration_minutes": 30
  }'
```

### Create Care Plan
```bash
curl -X POST http://localhost:8000/api/care-plans \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "123",
    "title": "Diabetes Management",
    "goals": ["Reduce A1C", "Improve diet"],
    "interventions": ["Monthly checkups", "Nutrition counseling"]
  }'
```

### Approve Request
```bash
curl -X POST http://localhost:8000/api/approvals/request-id/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approver_id": "approver-123",
    "reason": "Approved after review"
  }'
```

## Architecture Deep Dive

### Agent Orchestration Flow
1. User request → FastAPI endpoint
2. Input validation against policies
3. Route to appropriate agent
4. Agent executes with tool registry
5. Agent collaborates with supporting agents
6. Human approval if needed
7. Audit logging
8. Response to user

### Data Flow
1. Request → API Layer
2. Validation (RBAC, Policy)
3. Tool execution
4. Database persistence
5. Memory storage
6. Audit logging
7. Response construction

## Extending the System

### Add New Tool
```python
class NewTool(HealthcareTool):
    def __init__(self):
        super().__init__("NewTool", "Description")
    
    def operation(self, *args) -> Dict:
        # Implementation
        pass

# Register tool
TOOL_REGISTRY["new"] = NewTool()
```

### Add New Policy
```python
policy_engine.add_rule(PolicyRule(
    rule_id="NEW001",
    name="Policy Name",
    description="Description",
    rule_type="resource_type",
    condition="validation condition",
    severity="high"
))
```

### Add New Agent
```python
self.agents["new_agent"] = autogen.ConversableAgent(
    name="NewAgent",
    system_message="System prompt",
    llm_config=self.llm_config
)
```

## Production Checklist

- [ ] Configure production database
- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS appropriately
- [ ] Setup health checks
- [ ] Configure logging and monitoring
- [ ] Enable audit logging
- [ ] Setup database backups
- [ ] Configure rate limiting
- [ ] Enable request validation
- [ ] Setup error tracking (Sentry, etc.)
- [ ] Configure CI/CD pipeline
- [ ] Security audit
- [ ] Load testing

## Support & Troubleshooting

See [README.md](README.md) for full documentation.
