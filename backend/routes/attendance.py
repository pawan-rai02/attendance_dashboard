"""
Attendance API routes.
RESTful endpoints for attendance management.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    AttendanceRecordCreate, AttendanceRecordBulk, AttendanceRecordResponse,
    AttendanceSummary, SubjectWiseAttendance, MonthlyTrend,
    AttendanceTrendResponse, ErrorResponse
)
from services import AttendanceService, AnalyticsService

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post(
    "/",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        404: {"model": ErrorResponse, "description": "Student or Subject not found"}
    }
)
def mark_attendance(
    record_data: AttendanceRecordCreate,
    db: Session = Depends(get_db)
) -> AttendanceRecordResponse:
    """
    Mark attendance for a student in a subject.
    
    - **student_id**: ID of the student
    - **subject_id**: ID of the subject
    - **date**: Date of attendance
    - **is_present**: Present (true) or Absent (false)
    - **remarks**: Optional remarks
    """
    from models import Student, Subject
    
    # Validate student and subject exist
    if not db.query(Student).filter(Student.id == record_data.student_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {record_data.student_id} not found"
        )
    
    if not db.query(Subject).filter(Subject.id == record_data.subject_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {record_data.subject_id} not found"
        )
    
    service = AttendanceService(db)
    record = service.create(record_data)
    
    return AttendanceRecordResponse.model_validate(record)


@router.post(
    "/bulk",
    response_model=List[AttendanceRecordResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"}
    }
)
def mark_attendance_bulk(
    bulk_data: AttendanceRecordBulk,
    db: Session = Depends(get_db)
) -> List[AttendanceRecordResponse]:
    """
    Mark attendance for multiple records at once.
    
    Useful for importing attendance data or marking for entire class.
    Maximum 1000 records per request.
    """
    service = AttendanceService(db)
    records = service.create_bulk(bulk_data.records)
    
    return [AttendanceRecordResponse.model_validate(r) for r in records]


@router.get(
    "/student/{student_id}",
    response_model=List[AttendanceRecordResponse],
    responses={
        404: {"model": ErrorResponse, "description": "Student not found"}
    }
)
def get_student_attendance(
    student_id: int,
    subject_id: Optional[int] = Query(None, description="Filter by subject"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
) -> List[AttendanceRecordResponse]:
    """
    Get attendance records for a student.
    
    Optional filters:
    - **subject_id**: Filter by specific subject
    - **start_date**: Filter from this date
    - **end_date**: Filter to this date
    """
    service = AttendanceService(db)
    records = service.get_by_student(
        student_id=student_id,
        subject_id=subject_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return [AttendanceRecordResponse.model_validate(r) for r in records]


@router.get(
    "/subject/{subject_id}",
    response_model=List[AttendanceRecordResponse]
)
def get_subject_attendance(
    subject_id: int,
    date_filter: Optional[date] = Query(None, alias="date", description="Filter by specific date"),
    db: Session = Depends(get_db)
) -> List[AttendanceRecordResponse]:
    """
    Get attendance records for a subject.
    
    Useful for viewing class attendance on a specific day.
    """
    service = AttendanceService(db)
    records = service.get_by_subject(
        subject_id=subject_id,
        date=date_filter
    )
    
    return [AttendanceRecordResponse.model_validate(r) for r in records]


@router.put(
    "/{record_id}",
    response_model=AttendanceRecordResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Record not found"}
    }
)
def update_attendance(
    record_id: int,
    is_present: bool,
    remarks: Optional[str] = Query(None, description="Optional remarks"),
    db: Session = Depends(get_db)
) -> AttendanceRecordResponse:
    """
    Update an existing attendance record.
    
    Used to correct mistakenly marked attendance.
    """
    service = AttendanceService(db)
    record = service.update_record(
        record_id=record_id,
        is_present=is_present,
        remarks=remarks
    )
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with id {record_id} not found"
        )
    
    return AttendanceRecordResponse.model_validate(record)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Record not found"}
    }
)
def delete_attendance(
    record_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete an attendance record.
    
    Use with caution - this permanently removes the record.
    """
    service = AttendanceService(db)
    success = service.delete_record(record_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with id {record_id} not found"
        )


# ============== Analytics Endpoints ==============

@router.get(
    "/analytics/student/{student_id}/summary",
    response_model=AttendanceSummary,
    responses={
        404: {"model": ErrorResponse, "description": "Student not found"}
    }
)
def get_attendance_summary(
    student_id: int,
    db: Session = Depends(get_db)
) -> AttendanceSummary:
    """
    Get overall attendance summary for a student.
    
    Returns total classes, present count, percentage, and defaulter status.
    """
    service = AnalyticsService(db)
    return service.calculate_overall_attendance(student_id)


@router.get(
    "/analytics/student/{student_id}/subject-wise",
    response_model=List[SubjectWiseAttendance]
)
def get_subject_wise_attendance(
    student_id: int,
    db: Session = Depends(get_db)
) -> List[SubjectWiseAttendance]:
    """
    Get subject-wise attendance breakdown for a student.
    
    Shows attendance percentage for each subject separately.
    """
    service = AnalyticsService(db)
    return service.calculate_subject_wise_attendance(student_id)


@router.get(
    "/analytics/student/{student_id}/monthly-trend",
    response_model=List[MonthlyTrend]
)
def get_monthly_trend(
    student_id: int,
    months: int = Query(6, ge=1, le=24, description="Number of months to include"),
    db: Session = Depends(get_db)
) -> List[MonthlyTrend]:
    """
    Get monthly attendance trend for visualization.
    
    Returns attendance percentage for each month.
    """
    service = AnalyticsService(db)
    return service.calculate_monthly_trend(student_id, months=months)


@router.get(
    "/analytics/student/{student_id}/complete",
    response_model=AttendanceTrendResponse
)
def get_complete_attendance_trend(
    student_id: int,
    db: Session = Depends(get_db)
) -> AttendanceTrendResponse:
    """
    Get complete attendance analytics for a student.
    
    Combines overall summary, subject-wise breakdown, and monthly trend.
    """
    service = AnalyticsService(db)
    return service.get_attendance_trend(student_id)


@router.get(
    "/analytics/subject/{subject_id}/class-stats",
    responses={
        404: {"model": ErrorResponse, "description": "Subject not found"}
    }
)
def get_class_analytics(
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Get class-wide analytics for a subject.
    
    Shows average attendance, students at risk, and defaulter percentage.
    """
    from schemas import ClassAnalytics
    service = AnalyticsService(db)
    return service.get_class_analytics(subject_id)
