"""
SQLAlchemy models for the attendance database.
Normalized schema with proper foreign keys and indexing.
"""

from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Date, Float, ForeignKey,
    Index, DateTime, Boolean, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from database import Base


class Student(Base):
    """
    Student model - stores student information.
    Normalized design: student data separate from attendance records.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    department = Column(String(50), nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    enrollment_date = Column(Date, nullable=False, default=date.today)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_student_dept_semester', 'department', 'semester'),
        Index('idx_student_active', 'is_active'),
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, roll_number='{self.roll_number}', name='{self.name}')>"


class Subject(Base):
    """
    Subject model - stores subject/course information.
    """
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String(20), unique=True, nullable=False, index=True)
    subject_name = Column(String(150), nullable=False)
    department = Column(String(50), nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    credits = Column(Integer, nullable=False, default=4)
    total_classes_required = Column(Integer, default=60)  # For 75% calculation
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attendance_records = relationship("AttendanceRecord", back_populates="subject", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_subject_dept_semester', 'department', 'semester'),
    )

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, code='{self.subject_code}', name='{self.subject_name}')>"


class AttendanceRecord(Base):
    """
    Attendance record model - stores individual attendance entries.
    Composite unique constraint prevents duplicate records.
    """
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    is_present = Column(Boolean, nullable=False, default=True)
    remarks = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    subject = relationship("Subject", back_populates="attendance_records")

    # Constraints
    __table_args__ = (
        UniqueConstraint('student_id', 'subject_id', 'date', name='uq_student_subject_date'),
        Index('idx_attendance_student_date', 'student_id', 'date'),
        Index('idx_attendance_subject_date', 'subject_id', 'date'),
        CheckConstraint('is_present IN (0, 1)', name='check_is_present_boolean'),
    )

    def __repr__(self) -> str:
        return f"<AttendanceRecord(student_id={self.student_id}, subject_id={self.subject_id}, date={self.date}, present={self.is_present})>"


class ClassSchedule(Base):
    """
    Class schedule model - tracks planned classes for attendance calculation.
    Used to determine total classes held vs total classes required.
    """
    __tablename__ = "class_schedules"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    is_conducted = Column(Boolean, default=True)
    topic_covered = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subject = relationship("Subject")

    # Constraints
    __table_args__ = (
        UniqueConstraint('subject_id', 'date', name='uq_subject_schedule_date'),
        Index('idx_schedule_subject_date', 'subject_id', 'date'),
    )

    def __repr__(self) -> str:
        return f"<ClassSchedule(subject_id={self.subject_id}, date={self.date}, conducted={self.is_conducted})>"


class RiskAssessment(Base):
    """
    Risk assessment model - stores computed risk scores for students.
    Pre-computed for dashboard performance.
    """
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True)
    current_attendance_pct = Column(Float, nullable=False)
    required_attendance_pct = Column(Float, default=75.0)
    classes_remaining = Column(Integer, nullable=False)
    min_classes_needed = Column(Integer, nullable=False)
    is_at_risk = Column(Boolean, nullable=False, default=False)
    is_impossible = Column(Boolean, nullable=False, default=False)  # Mathematically impossible to reach 75%
    risk_score = Column(Float, nullable=False)  # 0-100, higher = more risk
    assessment_date = Column(Date, nullable=False, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student")
    subject = relationship("Subject")

    # Indexes
    __table_args__ = (
        Index('idx_risk_student_subject', 'student_id', 'subject_id'),
        Index('idx_risk_at_risk', 'is_at_risk'),
        Index('idx_risk_date', 'assessment_date'),
    )

    def __repr__(self) -> str:
        return f"<RiskAssessment(student_id={self.student_id}, risk_score={self.risk_score}, at_risk={self.is_at_risk})>"
