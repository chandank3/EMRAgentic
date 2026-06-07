# Healthcare Care Coordinator Agent - Setup Guide

## Quick Setup (5 minutes)

### Prerequisites
- Python 3.10+
- PostgreSQL
- Ollama

### Steps

1. **Extract and navigate**
   ```bash
   cd EMRAgentic
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment**
   ```bash
   cp .env.example .env
   ```

5. **Initialize database**
   ```bash
   python -c "from src.database import init_db; init_db()"
   ```

6. **Start Ollama** (in another terminal)
   ```bash
   ollama serve
   ollama pull mistral
   ```

7. **Run application**
   ```bash
   python -m uvicorn src.main:app --reload
   ```

8. **Access the API**
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

---

## Docker Setup (3 minutes)

```bash
docker-compose up -d
```

Wait for all services to be healthy:
```bash
docker-compose ps
```

Access at http://localhost:8000/docs

---

## Project Structure

```
EMRAgentic/
├── src/
│   ├── agents/              # AutoGen agent orchestration
│   │   └── orchestrator.py
│   ├── tools/               # Tool registry and definitions
│   │   └── tools.py
│   ├── models/              # SQLAlchemy ORM models
│   │   └── models.py
│   ├── database/            # Database setup and connection
│   │   └── __init__.py
│   ├── security/            # RBAC and PII masking
│   │   ├── rbac.py
│   │   └── pii_masking.py
│   ├── workflows/           # Approval workflows
│   │   └── approval.py
│   ├── memory/              # Agent memory management
│   │   └── memory.py
│   ├── policy/              # Policy engine
│   │   └── policy_engine.py
│   ├── config.py            # Configuration management
│   └── main.py              # FastAPI application
├── tests/                   # Test suite
│   └── test_security.py
├── migrations/              # Database migrations (Alembic)
├── docs/                    # Additional documentation
├── config/                  # Configuration files
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Container image
├── .env.example             # Environment template
├── README.md               # Main documentation
├── DEVELOPMENT.md          # Development guide
├── ARCHITECTURE.md         # Architecture & design patterns
└── demo.py                 # Demonstration script
```

---

## Key Features at a Glance

### 🤖 Agent Orchestration
- **Care Coordinator**: Main orchestrator
- **Clinical Support**: Evidence-based recommendations
- **Document Analyzer**: Medical record processing
- **Policy Compliance**: Rule validation
- **Escalation Manager**: Approval routing

### 🔐 Security & Compliance
- **RBAC**: 6 user roles with granular permissions
- **PII Masking**: 3 masking strategies
- **Audit Logging**: Comprehensive action tracking
- **Approval Workflows**: Human-in-the-loop for critical decisions
- **Policy Engine**: Configurable organizational policies

### 📋 Core Features
- Appointment booking with conflict detection
- Evidence-based care plan generation
- Medication reminder management
- Medical document retrieval with semantic search
- Automated visit summary generation
- Risk-based escalation

### 💾 Data Layer
- PostgreSQL for persistence
- pgvector for semantic search
- SQLAlchemy ORM with relationships
- Complete audit trail

---

## Common Tasks

### Run Demo
```bash
python demo.py
```

### Run Tests
```bash
pytest tests/ -v
```

### View Logs
```bash
tail -f logs/application.log
```

### Check Database
```bash
psql healthcare_coordinator
\dt  # List tables
```

### API Examples

**Schedule Appointment:**
```bash
curl -X POST http://localhost:8000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-123",
    "title": "Annual Checkup",
    "appointment_type": "checkup",
    "duration_minutes": 30,
    "scheduled_at": "2024-12-15T10:00:00"
  }'
```

**Create Care Plan:**
```bash
curl -X POST http://localhost:8000/api/care-plans \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-123",
    "plan_data": {
      "title": "Diabetes Management",
      "goals": ["Reduce A1C to <7%", "Weight loss"],
      "coordinator_id": "coord-123",
      "interventions": ["Monthly checkups", "Nutrition counseling"],
      "timeline": "3 months"
    }
  }'
```

**Get Pending Approvals:**
```bash
curl http://localhost:8000/api/approvals/pending
```

---

## Troubleshooting

### PostgreSQL Connection Error
```
Solution: 
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Create database: createdb healthcare_coordinator
```

### Ollama Connection Error
```
Solution:
- Start Ollama: ollama serve
- Pull model: ollama pull mistral
- Check OLLAMA_BASE_URL in .env
```

### Port Already in Use
```
Solution:
- Change API_PORT in .env
- Or kill process: lsof -i :8000 | kill -9 <PID>
```

### Import Errors
```
Solution:
- Ensure virtual environment is activated
- Reinstall dependencies: pip install -r requirements.txt
```

---

## Next Steps

1. **Explore the Code**
   - Read [ARCHITECTURE.md](ARCHITECTURE.md) for design patterns
   - Review agent orchestration in `src/agents/orchestrator.py`
   - Check policy engine in `src/policy/policy_engine.py`

2. **Run Demos**
   - Execute `python demo.py` to see features in action
   - Review demo output to understand system capabilities

3. **Try the API**
   - Visit http://localhost:8000/docs
   - Try endpoints interactively
   - Review request/response formats

4. **Understand the Data Model**
   - Review `src/models/models.py`
   - Understand relationships between entities
   - Check audit logging

5. **Extend the System**
   - Add new agents
   - Create new tools
   - Implement new policies
   - Add new roles

---

## Production Deployment

Before deploying to production:

- [ ] Update `SECRET_KEY` in .env
- [ ] Configure production database
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Setup monitoring and alerting
- [ ] Enable structured logging
- [ ] Configure backups
- [ ] Security audit
- [ ] Load testing
- [ ] Set up CI/CD pipeline

---

## Support & Resources

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **README**: [README.md](README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Development**: [DEVELOPMENT.md](DEVELOPMENT.md)

---

**Ready to build something great!** 🚀
