"""
CRUD services for basic database operations.
Provides clean separation of data access logic.
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import Student, Subject, AttendanceRecord
from schemas import (
    StudentCreate, StudentUpdate,
    SubjectCreate, SubjectUpdate,
    AttendanceRecordCreate
)


class StudentService:
    """Service for student CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: StudentCreate) -> Student:
        """Create a new student."""
        student = Student(
            roll_number=data.roll_number,
            name=data.name,
            email=data.email,
            department=data.department,
            semester=data.semester,
            enrollment_date=data.enrollment_date or date.today(),
            is_active=data.is_active
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def get_by_id(self, student_id: int) -> Optional[Student]:
        """Get student by ID."""
        return self.db.query(Student).filter(Student.id == student_id).first()

    def get_by_roll_number(self, roll_number: str) -> Optional[Student]:
        """Get student by roll number."""
        return self.db.query(Student).filter(Student.roll_number == roll_number).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        is_active: bool = True
    ) -> List[Student]:
        """Get all students with optional filters."""
        query = self.db.query(Student).filter(Student.is_active == is_active)
        
        if department:
            query = query.filter(Student.department == department)
        if semester:
            query = query.filter(Student.semester == semester)
        
        return query.offset(skip).limit(limit).all()

    def update(self, student_id: int, data: StudentUpdate) -> Optional[Student]:
        """Update student information."""
        student = self.get_by_id(student_id)
        if not student:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)

        self.db.commit()
        self.db.refresh(student)
        return student

    def delete(self, student_id: int) -> bool:
        """Soft delete a student (set is_active=False)."""
        student = self.get_by_id(student_id)
        if not student:
            return False
        
        student.is_active = False
        self.db.commit()
        return True

    def hard_delete(self, student_id: int) -> bool:
        """Permanently delete a student."""
        student = self.get_by_id(student_id)
        if not student:
            return False
        
        self.db.delete(student)
        self.db.commit()
        return True


class SubjectService:
    """Service for subject CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: SubjectCreate) -> Subject:
        """Create a new subject."""
        subject = Subject(
            subject_code=data.subject_code,
            subject_name=data.subject_name,
            department=data.department,
            semester=data.semester,
            credits=data.credits,
            total_classes_required=data.total_classes_required
        )
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        """Get subject by ID."""
        return self.db.query(Subject).filter(Subject.id == subject_id).first()

    def get_by_code(self, subject_code: str) -> Optional[Subject]:
        """Get subject by code."""
        return self.db.query(Subject).filter(Subject.subject_code == subject_code).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        department: Optional[str] = None,
        semester: Optional[int] = None
    ) -> List[Subject]:
        """Get all subjects with optional filters."""
        query = self.db.query(Subject)
        
        if department:
            query = query.filter(Subject.department == department)
        if semester:
            query = query.filter(Subject.semester == semester)
        
        return query.offset(skip).limit(limit).all()

    def update(self, subject_id: int, data: SubjectUpdate) -> Optional[Subject]:
        """Update subject information."""
        subject = self.get_by_id(subject_id)
        if not subject:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subject, field, value)

        self.db.commit()
        self.db.refresh(subject)
        return subject

    def delete(self, subject_id: int) -> bool:
        """Delete a subject."""
        subject = self.get_by_id(subject_id)
        if not subject:
            return False
        
        self.db.delete(subject)
        self.db.commit()
        return True


class AttendanceService:
    """Service for attendance record CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: AttendanceRecordCreate) -> AttendanceRecord:
        """Create a new attendance record."""
        # Check for duplicates
        existing = self.db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.student_id == data.student_id,
                AttendanceRecord.subject_id == data.subject_id,
                AttendanceRecord.date == data.attendance_date
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.is_present = data.is_present
            existing.remarks = data.remarks
            self.db.commit()
            self.db.refresh(existing)
            return existing

        record = AttendanceRecord(
            student_id=data.student_id,
            subject_id=data.subject_id,
            date=data.attendance_date,
            is_present=data.is_present,
            remarks=data.remarks
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def create_bulk(self, records: List[AttendanceRecordCreate]) -> List[AttendanceRecord]:
        """Create multiple attendance records efficiently."""
        created = []
        for data in records:
            record = self.create(data)
            created.append(record)
        return created

    def get_by_student(
        self,
        student_id: int,
        subject_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AttendanceRecord]:
        """Get attendance records for a student."""
        query = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student_id
        )
        
        if subject_id:
            query = query.filter(AttendanceRecord.subject_id == subject_id)
        if start_date:
            query = query.filter(AttendanceRecord.date >= start_date)
        if end_date:
            query = query.filter(AttendanceRecord.date <= end_date)
        
        return query.order_by(AttendanceRecord.date.desc()).all()

    def get_by_subject(
        self,
        subject_id: int,
        date: Optional[date] = None
    ) -> List[AttendanceRecord]:
        """Get attendance records for a subject."""
        query = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.subject_id == subject_id
        )
        
        if date:
            query = query.filter(AttendanceRecord.date == date)
        
        return query.all()

    def update_record(self, record_id: int, is_present: bool, remarks: Optional[str] = None) -> Optional[AttendanceRecord]:
        """Update an attendance record."""
        record = self.db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
        if not record:
            return None
        
        record.is_present = is_present
        if remarks is not None:
            record.remarks = remarks
        
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_record(self, record_id: int) -> bool:
        """Delete an attendance record."""
        record = self.db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
        if not record:
            return False
        
        self.db.delete(record)
        self.db.commit()
        return True

    def get_attendance_stats(
        self,
        student_id: int,
        subject_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get attendance statistics for a student."""
        from sqlalchemy import func
        
        filters = [AttendanceRecord.student_id == student_id]
        if subject_id:
            filters.append(AttendanceRecord.subject_id == subject_id)
        
        stats = self.db.query(
            func.count(AttendanceRecord.id).label('total'),
            func.sum(func.cast(AttendanceRecord.is_present, Integer)).label('present')
        ).filter(*filters).first()
        
        total = stats.total or 0
        present = stats.present or 0
        percentage = (present / total * 100) if total > 0 else 0.0
        
        return {
            'total_classes': total,
            'classes_present': present,
            'classes_absent': total - present,
            'attendance_percentage': round(percentage, 2),
            'is_defaulter': percentage < 75.0
        }


# Import Integer for the cast function
from sqlalchemy import Integer
