import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
import uuid
from src.config import get_settings
from sqlalchemy import create_engine, text

# We will use raw SQL to avoid dialect issues
settings = get_settings()
engine = create_engine(settings.database_url)

PATIENT_ID = "11111111-1111-1111-1111-111111111111"
COORD_ID = "22222222-2222-2222-2222-222222222222"

def init_tables():
    # To properly init tables in SQLite with SQLAlchemy, we need to import models first
    from src.database import Base, engine as db_engine
    import src.models.models
    Base.metadata.create_all(bind=db_engine)
    print("Tables created.")

def seed_data():
    with engine.begin() as conn:
        # Create Patient
        conn.execute(text("""
            INSERT INTO user (id, email, username, hashed_password, full_name, role, is_active, created_at, updated_at)
            VALUES (:id, :email, :username, :pwd, :name, :role, 1, :now, :now)
        """), {
            "id": PATIENT_ID,
            "email": "patient@example.com",
            "username": "patient123",
            "pwd": "hashed",
            "name": "Jane Doe",
            "role": "PATIENT",
            "now": datetime.utcnow()
        })
        
        # Create Coordinator
        conn.execute(text("""
            INSERT INTO user (id, email, username, hashed_password, full_name, role, is_active, department, created_at, updated_at)
            VALUES (:id, :email, :username, :pwd, :name, :role, 1, :dept, :now, :now)
        """), {
            "id": COORD_ID,
            "email": "coord@example.com",
            "username": "coord123",
            "pwd": "hashed",
            "name": "Dr. Sarah Johnson",
            "role": "CARE_COORDINATOR",
            "dept": "Cardiology",
            "now": datetime.utcnow()
        })

        # Create Appointment
        conn.execute(text("""
            INSERT INTO appointment (id, patient_id, scheduled_by_id, title, appointment_type, status, scheduled_at, duration_minutes, created_at, updated_at)
            VALUES (:id, :patient, :coord, :title, :type, :status, :scheduled, 30, :now, :now)
        """), {
            "id": str(uuid.uuid4()),
            "patient": PATIENT_ID,
            "coord": COORD_ID,
            "title": "Annual Checkup",
            "type": "checkup",
            "status": "SCHEDULED",
            "scheduled": datetime.utcnow() + timedelta(days=2),
            "now": datetime.utcnow()
        })

        # Create Care Plan
        conn.execute(text("""
            INSERT INTO care_plan (id, patient_id, coordinator_id, title, description, status, goals, interventions, created_at, updated_at)
            VALUES (:id, :patient, :coord, :title, :desc, :status, :goals, :interventions, :now, :now)
        """), {
            "id": str(uuid.uuid4()),
            "patient": PATIENT_ID,
            "coord": COORD_ID,
            "title": "Diabetes Management",
            "desc": "Manage Type 2 Diabetes",
            "status": "ACTIVE",
            "goals": '["Reduce A1C", "Improve Diet"]',
            "interventions": '["Monthly checkups"]',
            "now": datetime.utcnow()
        })

        # Create Medication
        conn.execute(text("""
            INSERT INTO medication (id, patient_id, name, dosage, frequency, route, start_date, is_active, created_at, updated_at)
            VALUES (:id, :patient, :name, :dosage, :freq, :route, :start, 1, :now, :now)
        """), {
            "id": str(uuid.uuid4()),
            "patient": PATIENT_ID,
            "name": "Metformin",
            "dosage": "500mg",
            "freq": "twice daily",
            "route": "oral",
            "start": datetime.utcnow() - timedelta(days=10),
            "now": datetime.utcnow()
        })

    print("Data seeded successfully.")

if __name__ == "__main__":
    init_tables()
    seed_data()
