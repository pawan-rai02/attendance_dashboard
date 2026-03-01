"""
Utility functions for the attendance dashboard.
Includes helpers, validators, and common operations.
"""

import re
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
from functools import wraps
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Time Complexity: O(n) where n = email length
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_roll_number(roll_number: str) -> bool:
    """
    Validate roll number format.
    Accepts formats like: 2024CS001, 24CSE001, etc.
    """
    pattern = r'^[A-Z0-9]{3,15}$'
    return re.match(pattern, roll_number.upper()) is not None


def validate_date_range(start_date: date, end_date: date) -> bool:
    """Validate that start date is before or equal to end date."""
    return start_date <= end_date


def get_date_range(
    start_date: date,
    end_date: date,
    exclude_weekends: bool = False
) -> List[date]:
    """
    Generate list of dates between start and end.
    
    Time Complexity: O(n) where n = number of days
    Space Complexity: O(n) for result list
    
    Args:
        start_date: Start of range
        end_date: End of range
        exclude_weekends: If True, skip Saturday and Sunday
        
    Returns:
        List of date objects
    """
    if not validate_date_range(start_date, end_date):
        raise ValueError("Start date must be before end date")
    
    dates = []
    current = start_date
    while current <= end_date:
        if exclude_weekends and current.weekday() >= 5:
            current += timedelta(days=1)
            continue
        dates.append(current)
        current += timedelta(days=1)
    
    return dates


def calculate_percentage(part: float, total: float, decimals: int = 2) -> float:
    """
    Calculate percentage with safe division.
    
    Time Complexity: O(1)
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, decimals)


def format_attendance_status(percentage: float) -> str:
    """
    Format attendance percentage into status string.
    
    Returns:
        Status string: 'Excellent', 'Good', 'Average', 'Poor', 'Critical'
    """
    if percentage >= 90:
        return 'Excellent'
    elif percentage >= 75:
        return 'Good'
    elif percentage >= 60:
        return 'Average'
    elif percentage >= 50:
        return 'Poor'
    else:
        return 'Critical'


def get_semester_dates(semester: int, year: int) -> Dict[str, date]:
    """
    Get approximate semester start and end dates.
    Adjust based on your institution's academic calendar.
    
    Assumes:
    - Odd semesters (1, 3, 5, 7): July to December
    - Even semesters (2, 4, 6, 8): January to June
    """
    if semester % 2 == 1:  # Odd semester
        start = date(year, 7, 1)
        end = date(year, 12, 15)
    else:  # Even semester
        start = date(year, 1, 15)
        end = date(year, 6, 30)
    
    return {'start': start, 'end': end}


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator for retrying failed operations.
    Useful for database operations and external API calls.
    
    Time Complexity: O(n * m) where n = retries, m = operation cost
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}"
                    )
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            
            logger.error(f"All {max_retries} attempts failed")
            raise last_exception
        return wrapper
    return decorator


def batch_process(
    items: List[Any],
    processor: Callable,
    batch_size: int = 100
) -> List[Any]:
    """
    Process items in batches to avoid memory issues.
    
    Time Complexity: O(n) where n = number of items
    Space Complexity: O(batch_size) for each batch
    
    Args:
        items: List of items to process
        processor: Function to process each batch
        batch_size: Number of items per batch
        
    Returns:
        List of processed results
    """
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_result = processor(batch)
        results.extend(batch_result)
    return results


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division that returns default on division by zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))


def generate_attendance_report_data(
    student_name: str,
    roll_number: str,
    attendance_data: List[Dict]
) -> Dict[str, Any]:
    """
    Generate formatted data for attendance report.
    
    Returns:
        Dictionary formatted for report generation
    """
    total_classes = sum(d.get('total', 0) for d in attendance_data)
    total_present = sum(d.get('present', 0) for d in attendance_data)
    overall_pct = safe_divide(total_present * 100, total_classes)
    
    return {
        'student_name': student_name,
        'roll_number': roll_number,
        'report_date': date.today().isoformat(),
        'summary': {
            'total_classes': total_classes,
            'total_present': total_present,
            'total_absent': total_classes - total_present,
            'attendance_percentage': round(overall_pct, 2),
            'status': format_attendance_status(overall_pct)
        },
        'subject_breakdown': attendance_data,
        'is_defaulter': overall_pct < 75.0
    }


class Timer:
    """Context manager for timing code execution."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, *args):
        self.end_time = datetime.now()
        self.elapsed = (self.end_time - self.start_time).total_seconds()
        logger.info(f"{self.name} completed in {self.elapsed:.4f} seconds")


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator for expensive computations.
    Only works with hashable arguments.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper
