"""
Analytics and Risk Assessment API routes.
Endpoints for dashboard data and risk predictions.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    RiskAssessmentResponse, RiskPredictionInput, RiskPredictionResponse,
    ClassAnalytics, DashboardSummary, ErrorResponse
)
from services import AnalyticsService, RiskAssessmentService, MLPredictionService

router = APIRouter(prefix="/analytics", tags=["Analytics & Risk"])


# ============== Dashboard Endpoints ==============

@router.get(
    "/dashboard/summary",
    response_model=DashboardSummary
)
def get_dashboard_summary(
    db: Session = Depends(get_db)
) -> DashboardSummary:
    """
    Get overall dashboard summary.
    
    Returns key metrics:
    - Total students and subjects
    - Overall attendance average
    - Total defaulters
    - Students at high risk
    """
    service = AnalyticsService(db)
    return service.get_dashboard_summary()


@router.get(
    "/dashboard/defaulters",
    response_model=List[dict]
)
def get_defaulters(
    limit: int = Query(50, ge=1, le=200, description="Maximum defaulters to return"),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get list of students who are defaulters (< 75% attendance).
    
    Sorted by attendance percentage (lowest first).
    """
    service = AnalyticsService(db)
    return service.get_defaulters_list(limit=limit)


# ============== Risk Assessment Endpoints ==============

@router.get(
    "/risk/student/{student_id}",
    response_model=RiskAssessmentResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Student not found"}
    }
)
def get_student_risk(
    student_id: int,
    subject_id: Optional[int] = Query(None, description="Optional subject-specific risk"),
    db: Session = Depends(get_db)
) -> RiskAssessmentResponse:
    """
    Get risk assessment for a student.
    
    Calculates:
    - Current attendance percentage
    - Classes remaining
    - Minimum classes needed to reach 75%
    - Whether it's mathematically possible
    - Risk score (0-100)
    - Actionable recommendation
    """
    service = RiskAssessmentService(db)
    return service.calculate_risk_for_student(student_id, subject_id)


@router.get(
    "/risk/all-at-risk",
    response_model=List[RiskAssessmentResponse]
)
def get_all_at_risk_students(
    subject_id: Optional[int] = Query(None, description="Filter by subject"),
    db: Session = Depends(get_db)
) -> List[RiskAssessmentResponse]:
    """
    Get all students currently at risk.
    
    Returns students with attendance below 75% or at risk of falling below.
    Sorted by risk score (highest first).
    """
    service = RiskAssessmentService(db)
    return service.get_all_at_risk_students(subject_id)


@router.post(
    "/risk/predict",
    response_model=RiskPredictionResponse
)
def predict_attendance_risk(
    prediction_input: RiskPredictionInput,
    db: Session = Depends(get_db)
) -> RiskPredictionResponse:
    """
    Predict probability of attendance shortage using ML.
    
    Uses Logistic Regression to predict probability of falling below 75%.
    
    Input features:
    - **current_attendance_pct**: Current attendance percentage
    - **classes_attended**: Number of classes attended so far
    - **classes_remaining**: Number of classes remaining
    - **subject_difficulty**: Optional difficulty score (0-1)
    - **historical_attendance_trend**: Optional trend coefficient (-1 to 1)
    
    Returns:
    - **probability_of_shortage**: Probability of falling below 75%
    - **risk_category**: Low/Medium/High
    - **confidence**: Model confidence
    - **feature_importance**: Which features matter most
    """
    service = MLPredictionService()
    return service.predict_risk(prediction_input)


# ============== Class Analytics Endpoints ==============

@router.get(
    "/class/subject/{subject_id}",
    response_model=ClassAnalytics
)
def get_subject_class_analytics(
    subject_id: int,
    db: Session = Depends(get_db)
) -> ClassAnalytics:
    """
    Get class-wide analytics for a specific subject.
    
    Shows:
    - Total students with attendance
    - Average attendance percentage
    - Students at risk vs safe
    - Defaulter percentage
    """
    service = AnalyticsService(db)
    return service.get_class_analytics(subject_id)


@router.get(
    "/class/all-subjects",
    response_model=List[ClassAnalytics]
)
def get_all_subjects_analytics(
    db: Session = Depends(get_db)
) -> List[ClassAnalytics]:
    """
    Get analytics for all subjects.
    
    Useful for department-level overview.
    """
    from models import Subject
    
    subjects = db.query(Subject).all()
    service = AnalyticsService(db)
    
    analytics = []
    for subject in subjects:
        try:
            analytics.append(service.get_class_analytics(subject.id))
        except Exception:
            continue
    
    return analytics
