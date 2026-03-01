"""
Pydantic schemas for API request/response validation.
Provides type safety and automatic documentation.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator


# ============== Student Schemas ==============

class StudentBase(BaseModel):
    """Base schema for student data."""
    roll_number: str = Field(..., min_length=1, max_length=20, description="Unique roll number")
    name: str = Field(..., min_length=1, max_length=100, description="Student full name")
    email: EmailStr = Field(..., description="Student email address")
    department: str = Field(..., min_length=1, max_length=50, description="Department name")
    semester: int = Field(..., ge=1, le=8, description="Semester number (1-8)")


class StudentCreate(StudentBase):
    """Schema for creating a student."""
    enrollment_date: Optional[date] = None
    is_active: bool = True


class StudentUpdate(BaseModel):
    """Schema for updating a student."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    semester: Optional[int] = Field(None, ge=1, le=8)
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    """Schema for student response."""
    id: int
    enrollment_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============== Subject Schemas ==============

class SubjectBase(BaseModel):
    """Base schema for subject data."""
    subject_code: str = Field(..., min_length=1, max_length=20, description="Unique subject code")
    subject_name: str = Field(..., min_length=1, max_length=150, description="Subject name")
    department: str = Field(..., min_length=1, max_length=50, description="Department offering subject")
    semester: int = Field(..., ge=1, le=8, description="Semester for subject")
    credits: int = Field(..., ge=1, le=6, description="Subject credits")
    total_classes_required: int = Field(default=60, ge=30, le=120, description="Total classes for the course")


class SubjectCreate(SubjectBase):
    """Schema for creating a subject."""
    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject."""
    subject_name: Optional[str] = Field(None, min_length=1, max_length=150)
    credits: Optional[int] = Field(None, ge=1, le=6)
    total_classes_required: Optional[int] = Field(None, ge=30, le=120)


class SubjectResponse(SubjectBase):
    """Schema for subject response."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============== Attendance Record Schemas ==============

class AttendanceRecordBase(BaseModel):
    """Base schema for attendance record."""
    student_id: int = Field(..., gt=0, description="Student ID")
    subject_id: int = Field(..., gt=0, description="Subject ID")
    attendance_date: date = Field(..., description="Attendance date")
    is_present: bool = Field(..., description="Present or absent")
    remarks: Optional[str] = Field(None, max_length=255, description="Optional remarks")


class AttendanceRecordCreate(AttendanceRecordBase):
    """Schema for creating attendance record."""
    pass


class AttendanceRecordBulk(BaseModel):
    """Schema for bulk attendance creation."""
    records: List[AttendanceRecordCreate] = Field(..., min_length=1, max_length=1000)


class AttendanceRecordResponse(BaseModel):
    """Schema for attendance record response."""
    id: int
    student_id: int
    subject_id: int
    date: date
    is_present: bool
    remarks: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============== Attendance Analytics Schemas ==============

class AttendanceSummary(BaseModel):
    """Summary of attendance for a student."""
    student_id: int
    student_name: str
    roll_number: str
    total_classes: int
    classes_present: int
    attendance_percentage: float = Field(..., ge=0, le=100)
    is_defaulter: bool = Field(..., description="True if attendance < 75%")


class SubjectWiseAttendance(BaseModel):
    """Subject-wise attendance breakdown."""
    subject_id: int
    subject_code: str
    subject_name: str
    total_classes: int
    classes_present: int
    attendance_percentage: float
    is_defaulter: bool


class MonthlyTrend(BaseModel):
    """Monthly attendance trend data."""
    month: str  # Format: YYYY-MM
    total_classes: int
    classes_present: int
    attendance_percentage: float


class AttendanceTrendResponse(BaseModel):
    """Complete attendance trend response."""
    student_id: int
    student_name: str
    overall_attendance: float
    subject_wise: List[SubjectWiseAttendance]
    monthly_trend: List[MonthlyTrend]


# ============== Risk Assessment Schemas ==============

class RiskAssessmentBase(BaseModel):
    """Base risk assessment data."""
    student_id: int
    student_name: str
    subject_id: Optional[int] = None
    subject_name: Optional[str] = None
    current_attendance_pct: float
    required_attendance_pct: float = 75.0
    classes_remaining: int
    min_classes_needed: int
    is_at_risk: bool
    is_impossible: bool
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")


class RiskAssessmentResponse(RiskAssessmentBase):
    """Risk assessment with recommendations."""
    recommendation: str = Field(..., description="Actionable recommendation")
    assessment_date: date


class RiskPredictionInput(BaseModel):
    """Input for ML-based risk prediction."""
    current_attendance_pct: float
    classes_attended: int
    classes_remaining: int
    subject_difficulty: Optional[float] = Field(None, ge=0, le=1, description="Subject difficulty score")
    historical_attendance_trend: Optional[float] = Field(None, ge=-1, le=1, description="Trend coefficient")


class RiskPredictionResponse(BaseModel):
    """ML-based risk prediction response."""
    probability_of_shortage: float = Field(..., ge=0, le=1, description="Probability of falling below 75%")
    risk_category: str = Field(..., description="Low/Medium/High risk category")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")
    feature_importance: Optional[dict] = None


# ============== Class Analytics Schemas ==============

class ClassAnalytics(BaseModel):
    """Class-wide analytics for a subject."""
    subject_id: int
    subject_code: str
    subject_name: str
    total_students: int
    average_attendance: float
    students_at_risk: int
    students_safe: int
    defaulter_percentage: float


class DashboardSummary(BaseModel):
    """Overall dashboard summary."""
    total_students: int
    total_subjects: int
    overall_attendance_avg: float
    total_defaulters: int
    students_at_high_risk: int
    last_updated: datetime


# ============== Error Response Schema ==============

class ErrorResponse(BaseModel):
    """Standard error response format."""
    status_code: int
    message: str
    detail: Optional[str] = None


# ============== Pagination Schema ==============

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int
