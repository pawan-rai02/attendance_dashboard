"""
Test suite for Attendance Analytics Dashboard API.
Run with: pytest tests/ -v --cov=backend
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Base, get_db
from backend.main import app


# ===========================================
# Test Fixtures
# ===========================================

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ===========================================
# Student API Tests
# ===========================================

class TestStudentAPI:
    """Tests for Student endpoints."""
    
    def test_create_student(self, client):
        """Test creating a new student."""
        response = client.post(
            "/api/v1/students/",
            json={
                "roll_number": "TEST001",
                "name": "Test Student",
                "email": "test@college.edu",
                "department": "Computer Science",
                "semester": 3
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["roll_number"] == "TEST001"
        assert data["name"] == "Test Student"
        assert data["is_active"] == True
    
    def test_create_duplicate_roll_number(self, client, db_session):
        """Test creating student with duplicate roll number."""
        from backend.models import Student
        from datetime import date
        
        student = Student(
            roll_number="DUP001",
            name="Existing Student",
            email="existing@college.edu",
            department="CS",
            semester=1,
            enrollment_date=date.today()
        )
        db_session.add(student)
        db_session.commit()
        
        response = client.post(
            "/api/v1/students/",
            json={
                "roll_number": "DUP001",
                "name": "New Student",
                "email": "new@college.edu",
                "department": "CS",
                "semester": 1
            }
        )
        assert response.status_code == 409
    
    def test_get_students(self, client, db_session):
        """Test getting list of students."""
        from backend.models import Student
        from datetime import date
        
        student = Student(
            roll_number="LIST001",
            name="List Student",
            email="list@college.edu",
            department="CS",
            semester=1,
            enrollment_date=date.today()
        )
        db_session.add(student)
        db_session.commit()
        
        response = client.get("/api/v1/students/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1
    
    def test_get_student_not_found(self, client):
        """Test getting non-existent student."""
        response = client.get("/api/v1/students/99999")
        assert response.status_code == 404


# ===========================================
# Subject API Tests
# ===========================================

class TestSubjectAPI:
    """Tests for Subject endpoints."""
    
    def test_create_subject(self, client):
        """Test creating a new subject."""
        response = client.post(
            "/api/v1/subjects/",
            json={
                "subject_code": "CS101",
                "subject_name": "Introduction to Programming",
                "department": "Computer Science",
                "semester": 1,
                "credits": 4,
                "total_classes_required": 60
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["subject_code"] == "CS101"
    
    def test_get_subjects(self, client):
        """Test getting list of subjects."""
        response = client.get("/api/v1/subjects/")
        assert response.status_code == 200


# ===========================================
# Attendance API Tests
# ===========================================

class TestAttendanceAPI:
    """Tests for Attendance endpoints."""
    
    @pytest.fixture
    def setup_student_subject(self, db_session):
        """Create test student and subject."""
        from backend.models import Student, Subject
        from datetime import date
        
        student = Student(
            roll_number="ATT001",
            name="Attendance Test",
            email="att@college.edu",
            department="CS",
            semester=1,
            enrollment_date=date.today()
        )
        subject = Subject(
            subject_code="ATT101",
            subject_name="Test Subject",
            department="CS",
            semester=1,
            credits=4
        )
        db_session.add(student)
        db_session.add(subject)
        db_session.commit()
        
        return student.id, subject.id
    
    def test_mark_attendance(self, client, setup_student_subject):
        """Test marking attendance."""
        student_id, subject_id = setup_student_subject
        
        from datetime import date, timedelta
        
        response = client.post(
            "/api/v1/attendance/",
            json={
                "student_id": student_id,
                "subject_id": subject_id,
                "date": (date.today() - timedelta(days=1)).isoformat(),
                "is_present": True
            }
        )
        assert response.status_code == 201
    
    def test_get_student_attendance(self, client, setup_student_subject):
        """Test getting student attendance."""
        student_id, subject_id = setup_student_subject
        
        response = client.get(f"/api/v1/attendance/student/{student_id}")
        assert response.status_code == 200


# ===========================================
# Analytics API Tests
# ===========================================

class TestAnalyticsAPI:
    """Tests for Analytics endpoints."""
    
    def test_dashboard_summary(self, client):
        """Test getting dashboard summary."""
        response = client.get("/api/v1/analytics/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_students" in data
        assert "total_subjects" in data
        assert "overall_attendance_avg" in data
    
    def test_risk_assessment(self, client, db_session):
        """Test risk assessment endpoint."""
        from backend.models import Student, Subject, AttendanceRecord
        from datetime import date, timedelta
        
        # Create student with low attendance
        student = Student(
            roll_number="RISK001",
            name="Risk Test",
            email="risk@college.edu",
            department="CS",
            semester=1,
            enrollment_date=date.today()
        )
        subject = Subject(
            subject_code="RISK101",
            subject_name="Risk Subject",
            department="CS",
            semester=1,
            credits=4
        )
        db_session.add(student)
        db_session.add(subject)
        db_session.commit()
        
        # Add attendance records (40% attendance)
        for i in range(10):
            record = AttendanceRecord(
                student_id=student.id,
                subject_id=subject.id,
                date=date.today() - timedelta(days=i),
                is_present=(i < 4)  # 4 present, 6 absent
            )
            db_session.add(record)
        db_session.commit()
        
        response = client.get(f"/api/v1/analytics/risk/student/{student.id}")
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "is_at_risk" in data


# ===========================================
# ML Prediction Tests
# ===========================================

class TestMLPrediction:
    """Tests for ML prediction endpoint."""
    
    def test_predict_risk(self, client):
        """Test ML risk prediction."""
        response = client.post(
            "/api/v1/analytics/risk/predict",
            json={
                "current_attendance_pct": 65.0,
                "classes_attended": 40,
                "classes_remaining": 20,
                "subject_difficulty": 0.6,
                "historical_attendance_trend": -0.1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "probability_of_shortage" in data
        assert "risk_category" in data
        assert data["risk_category"] in ["Low", "Medium", "High"]


# ===========================================
# Health Check Tests
# ===========================================

class TestHealthCheck:
    """Tests for health check endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data


# ===========================================
# Validation Tests
# ===========================================

class TestValidation:
    """Tests for input validation."""
    
    def test_invalid_email(self, client):
        """Test invalid email validation."""
        response = client.post(
            "/api/v1/students/",
            json={
                "roll_number": "VAL001",
                "name": "Validation Test",
                "email": "invalid-email",
                "department": "CS",
                "semester": 1
            }
        )
        assert response.status_code == 422
    
    def test_invalid_semester(self, client):
        """Test invalid semester validation."""
        response = client.post(
            "/api/v1/students/",
            json={
                "roll_number": "VAL002",
                "name": "Validation Test",
                "email": "valid@college.edu",
                "department": "CS",
                "semester": 10  # Invalid: should be 1-8
            }
        )
        assert response.status_code == 422


# ===========================================
# Run Tests
# ===========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
