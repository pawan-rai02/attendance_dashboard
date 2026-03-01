"""
Analytics service for computing attendance statistics and trends.
Uses SQLAlchemy for efficient data processing.
"""

from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, Integer

from models import Student, Subject, AttendanceRecord, ClassSchedule, RiskAssessment
from schemas import (
    AttendanceSummary, SubjectWiseAttendance, MonthlyTrend,
    AttendanceTrendResponse, ClassAnalytics, DashboardSummary
)


class AnalyticsService:
    """
    Service class for attendance analytics computations.
    Optimized for performance with proper indexing usage.
    """

    ATTENDANCE_THRESHOLD = 75.0  # Minimum required attendance percentage

    def __init__(self, db: Session):
        self.db = db

    def calculate_overall_attendance(self, student_id: int) -> AttendanceSummary:
        """
        Calculate overall attendance percentage for a student.
        
        Time Complexity: O(log n) with proper indexing on student_id
        Space Complexity: O(1) - single aggregation query
        
        Args:
            student_id: ID of the student
            
        Returns:
            AttendanceSummary with overall attendance stats
        """
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student with id {student_id} not found")

        # Aggregate attendance using SQL for efficiency
        stats = self.db.query(
            func.count(AttendanceRecord.id).label('total'),
            func.sum(func.cast(AttendanceRecord.is_present, Integer)).label('present')
        ).filter(
            AttendanceRecord.student_id == student_id
        ).first()

        total_classes = stats.total or 0
        classes_present = stats.present or 0
        attendance_pct = (classes_present / total_classes * 100) if total_classes > 0 else 0.0

        return AttendanceSummary(
            student_id=student_id,
            student_name=student.name,
            roll_number=student.roll_number,
            total_classes=total_classes,
            classes_present=classes_present,
            attendance_percentage=round(attendance_pct, 2),
            is_defaulter=attendance_pct < self.ATTENDANCE_THRESHOLD
        )

    def calculate_subject_wise_attendance(self, student_id: int) -> List[SubjectWiseAttendance]:
        """
        Calculate attendance percentage for each subject.
        
        Time Complexity: O(m * log n) where m = number of subjects
        Space Complexity: O(m) for result list
        
        Args:
            student_id: ID of the student
            
        Returns:
            List of SubjectWiseAttendance for all subjects
        """
        # Join attendance with subjects and aggregate
        query = self.db.query(
            Subject.id,
            Subject.subject_code,
            Subject.subject_name,
            func.count(AttendanceRecord.id).label('total'),
            func.sum(func.cast(AttendanceRecord.is_present, Integer)).label('present')
        ).join(
            AttendanceRecord,
            AttendanceRecord.subject_id == Subject.id
        ).filter(
            AttendanceRecord.student_id == student_id
        ).group_by(
            Subject.id, Subject.subject_code, Subject.subject_name
        ).all()

        result = []
        for row in query:
            total = row.total or 0
            present = row.present or 0
            pct = (present / total * 100) if total > 0 else 0.0
            
            result.append(SubjectWiseAttendance(
                subject_id=row.id,
                subject_code=row.subject_code,
                subject_name=row.subject_name,
                total_classes=total,
                classes_present=present,
                attendance_percentage=round(pct, 2),
                is_defaulter=pct < self.ATTENDANCE_THRESHOLD
            ))
        
        return result

    def calculate_monthly_trend(self, student_id: int, months: int = 6) -> List[MonthlyTrend]:
        """
        Calculate monthly attendance trend for visualization.
        
        Time Complexity: O(n) where n = number of attendance records
        Space Complexity: O(m) where m = number of months
        
        Args:
            student_id: ID of the student
            months: Number of months to include in trend
            
        Returns:
            List of MonthlyTrend data points
        """
        # Query attendance with month extraction
        query = self.db.query(
            extract('year', AttendanceRecord.date).label('year'),
            extract('month', AttendanceRecord.date).label('month'),
            func.count(AttendanceRecord.id).label('total'),
            func.sum(func.cast(AttendanceRecord.is_present, Integer)).label('present')
        ).filter(
            AttendanceRecord.student_id == student_id
        ).group_by(
            extract('year', AttendanceRecord.date),
            extract('month', AttendanceRecord.date)
        ).order_by(
            extract('year', AttendanceRecord.date).desc(),
            extract('month', AttendanceRecord.date).desc()
        ).limit(months).all()

        # Reverse to get chronological order and format
        result = []
        for row in reversed(query):
            month_str = f"{int(row.year):04d}-{int(row.month):02d}"
            total = row.total or 0
            present = row.present or 0
            pct = (present / total * 100) if total > 0 else 0.0
            
            result.append(MonthlyTrend(
                month=month_str,
                total_classes=total,
                classes_present=present,
                attendance_percentage=round(pct, 2)
            ))
        
        return result

    def get_attendance_trend(self, student_id: int) -> AttendanceTrendResponse:
        """
        Get complete attendance trend for a student.
        Combines overall, subject-wise, and monthly data.
        
        Time Complexity: O(n + m) where n = records, m = subjects
        Space Complexity: O(n + m) for combined result
        
        Args:
            student_id: ID of the student
            
        Returns:
            Complete AttendanceTrendResponse
        """
        overall = self.calculate_overall_attendance(student_id)
        subject_wise = self.calculate_subject_wise_attendance(student_id)
        monthly = self.calculate_monthly_trend(student_id)

        return AttendanceTrendResponse(
            student_id=student_id,
            student_name=overall.student_name,
            overall_attendance=overall.attendance_percentage,
            subject_wise=subject_wise,
            monthly_trend=monthly
        )

    def get_class_analytics(self, subject_id: int) -> ClassAnalytics:
        """
        Get class-wide analytics for a subject.
        
        Time Complexity: O(s * log a) where s = students, a = attendance records
        Space Complexity: O(s) for student aggregation
        
        Args:
            subject_id: ID of the subject
            
        Returns:
            ClassAnalytics with aggregate statistics
        """
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise ValueError(f"Subject with id {subject_id} not found")

        # Get all students with attendance in this subject
        stats = self.db.query(
            AttendanceRecord.student_id,
            func.count(AttendanceRecord.id).label('total'),
            func.sum(func.cast(AttendanceRecord.is_present, Integer)).label('present')
        ).filter(
            AttendanceRecord.subject_id == subject_id
        ).group_by(
            AttendanceRecord.student_id
        ).all()

        if not stats:
            return ClassAnalytics(
                subject_id=subject_id,
                subject_code=subject.subject_code,
                subject_name=subject.subject_name,
                total_students=0,
                average_attendance=0.0,
                students_at_risk=0,
                students_safe=0,
                defaulter_percentage=0.0
            )

        # Calculate per-student percentages
        percentages = []
        at_risk = 0
        safe = 0
        
        for row in stats:
            pct = (row.present / row.total * 100) if row.total > 0 else 0.0
            percentages.append(pct)
            if pct < self.ATTENDANCE_THRESHOLD:
                at_risk += 1
            else:
                safe += 1

        avg_attendance = sum(percentages) / len(percentages) if percentages else 0.0
        defaulter_pct = (at_risk / len(stats) * 100) if stats else 0.0

        return ClassAnalytics(
            subject_id=subject_id,
            subject_code=subject.subject_code,
            subject_name=subject.subject_name,
            total_students=len(stats),
            average_attendance=round(avg_attendance, 2),
            students_at_risk=at_risk,
            students_safe=safe,
            defaulter_percentage=round(defaulter_pct, 2)
        )

    def get_dashboard_summary(self) -> DashboardSummary:
        """
        Get overall dashboard summary statistics.
        
        Time Complexity: O(n) for aggregation queries
        Space Complexity: O(1)
        
        Returns:
            DashboardSummary with key metrics
        """
        # Total students and subjects
        total_students = self.db.query(func.count(Student.id)).filter(Student.is_active == True).scalar()
        total_subjects = self.db.query(func.count(Subject.id)).scalar()

        # Overall attendance average
        overall_stats = self.db.query(
            func.count(AttendanceRecord.id).label('total'),
            func.sum(func.cast(AttendanceRecord.is_present, Integer)).label('present')
        ).first()

        overall_avg = 0.0
        if overall_stats and overall_stats.total > 0:
            overall_avg = (overall_stats.present / overall_stats.total) * 100

        # Count defaulters (students with < 75% overall attendance)
        student_attendance = self.db.query(
            AttendanceRecord.student_id,
            func.count(AttendanceRecord.id).label('total'),
            func.sum(func.cast(AttendanceRecord.is_present, Integer)).label('present')
        ).group_by(AttendanceRecord.student_id).all()

        defaulters = 0
        high_risk = 0
        
        for row in student_attendance:
            pct = (row.present / row.total * 100) if row.total > 0 else 0.0
            if pct < self.ATTENDANCE_THRESHOLD:
                defaulters += 1
                if pct < 50:
                    high_risk += 1

        return DashboardSummary(
            total_students=total_students or 0,
            total_subjects=total_subjects or 0,
            overall_attendance_avg=round(overall_avg, 2),
            total_defaulters=defaulters,
            students_at_high_risk=high_risk,
            last_updated=datetime.utcnow()
        )

    def get_defaulters_list(self, limit: int = 50) -> List[Dict]:
        """
        Get list of students who are defaulters (< 75% attendance).
        
        Time Complexity: O(n log n) for sorting
        Space Complexity: O(k) where k = number of defaulters
        
        Args:
            limit: Maximum number of defaulters to return
            
        Returns:
            List of defaulter student data
        """
        # Use subquery to calculate per-student attendance
        subquery = self.db.query(
            AttendanceRecord.student_id,
            func.count(AttendanceRecord.id).label('total'),
            func.sum(func.cast(AttendanceRecord.is_present, Integer)).label('present')
        ).group_by(AttendanceRecord.student_id).subquery()

        defaulters = self.db.query(
            Student.id,
            Student.roll_number,
            Student.name,
            Student.department,
            Student.email,
            (subquery.c.present / subquery.c.total * 100).label('attendance_pct')
        ).join(
            subquery,
            Student.id == subquery.c.student_id
        ).filter(
            (subquery.c.present / subquery.c.total * 100) < self.ATTENDANCE_THRESHOLD,
            Student.is_active == True
        ).order_by(
            (subquery.c.present / subquery.c.total * 100).asc()
        ).limit(limit).all()

        return [
            {
                'id': d.id,
                'roll_number': d.roll_number,
                'name': d.name,
                'department': d.department,
                'email': d.email,
                'attendance_percentage': round(d.attendance_pct, 2)
            }
            for d in defaulters
        ]


# Import Integer for the cast function
from sqlalchemy import Integer
