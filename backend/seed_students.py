from datetime import date, timedelta
import random

from sqlalchemy.orm import Session

from database import engine
from models import Student, Subject, AttendanceRecord, ClassSchedule, RiskAssessment


def seed_students() -> None:
    """
    Manually seed a structured 1000-student dataset with controlled attendance bands,
    future classes, and simple trend patterns.

    Usage (from backend directory):
        python -m seed_students
    """
    band_config = [
        # (label, count, min_pct, max_pct)
        ("critical", 140, 40, 59),
        ("at_risk", 150, 60, 64),
        ("borderline", 400, 65, 75),
        ("stable", 200, 76, 85),
        ("excellent", 110, 86, 95),
    ]

    total_target = sum(b[1] for b in band_config)
    assert total_target == 1000, "Band counts must add up to 1000"

    departments = [
        ("Computer Science", "CS", 3),
        ("Electrical Eng", "EE", 3),
        ("Mechanical Eng", "ME", 3),
    ]

    with Session(engine) as session:
        # Wipe existing student-related data
        session.query(RiskAssessment).delete()
        session.query(ClassSchedule).delete()
        session.query(AttendanceRecord).delete()
        session.query(Student).delete()
        session.commit()

        # Ensure a small, fixed subject set exists
        subjects = session.query(Subject).all()
        if not subjects:
            subjects_data = [
                ("CS301", "Data Structures", "Computer Science", 3, 4, 60),
                ("CS302", "Database Management", "Computer Science", 3, 4, 60),
                ("CS303", "Computer Networks", "Computer Science", 3, 3, 45),
                ("EE301", "Digital Electronics", "Electrical Eng", 3, 4, 60),
                ("ME301", "Thermodynamics", "Mechanical Eng", 3, 4, 60),
            ]
            for code, name, dept, sem, credits, total_required in subjects_data:
                session.add(
                    Subject(
                        subject_code=code,
                        subject_name=name,
                        department=dept,
                        semester=sem,
                        credits=credits,
                        total_classes_required=total_required,
                    )
                )
            session.commit()
            subjects = session.query(Subject).all()

        # Build 1000 students with band + trend assignment
        all_students = []
        roll_counter = 1
        trends = ["improving", "declining", "stable"]

        for label, count, min_pct, max_pct in band_config:
            for _ in range(count):
                dept_name, code, semester = random.choice(departments)
                roll = f"2024{code}{roll_counter:03d}"
                trend = random.choice(trends)
                target_pct = random.uniform(min_pct, max_pct)

                student = Student(
                    roll_number=roll,
                    name=f"{label.title()} Student {code}{roll_counter:03d}",
                    email=f"{roll.lower()}@college.edu",
                    department=dept_name,
                    semester=semester,
                )
                session.add(student)
                session.flush()

                all_students.append(
                    {
                        "instance": student,
                        "band": label,
                        "target_pct": target_pct,
                        "trend": trend,
                    }
                )
                roll_counter += 1

        session.commit()

        # Map subjects per department
        dept_subjects = {
            "Computer Science": [s for s in subjects if s.subject_code.startswith("CS3")],
            "Electrical Eng": [s for s in subjects if s.subject_code.startswith("EE3")],
            "Mechanical Eng": [s for s in subjects if s.subject_code.startswith("ME3")],
        }

        today = date.today()
        history_days = 90

        # Create past attendance with simple trends and controlled band percentages
        for entry in all_students:
            student = entry["instance"]
            target_pct = entry["target_pct"]
            trend = entry["trend"]

            student_subjects = dept_subjects.get(student.department) or subjects
            for subject in student_subjects:
                total_slots = 0
                present_count = 0

                # Distribute presence probabilities over time based on trend
                for days_ago in range(history_days):
                    if days_ago % 7 >= 5:
                        continue  # skip weekends

                    record_date = today - timedelta(days=days_ago)
                    total_slots += 1

                    # Base probability from target band
                    base_p = target_pct / 100.0

                    # Trend modulation: older dates slightly lower/higher
                    progress = 1.0 - (days_ago / history_days)
                    if trend == "improving":
                        p = min(0.98, base_p * (0.85 + 0.3 * progress))
                    elif trend == "declining":
                        p = max(0.05, base_p * (0.85 + 0.3 * (1.0 - progress)))
                    else:  # stable
                        p = base_p

                    is_present = random.random() < p
                    if is_present:
                        present_count += 1

                    session.add(
                        AttendanceRecord(
                            student_id=student.id,
                            subject_id=subject.id,
                            date=record_date,
                            is_present=is_present,
                            remarks=None if is_present else "Absent",
                        )
                    )

                # Small adjustment: if realized percentage deviates a lot, no further correction
                # (analytics services work off actual data, which will still respect the band roughly)

        session.commit()

        # Future classes: 15–20 per subject from tomorrow onward
        for subject in subjects:
            future_classes = random.randint(15, 20)
            for offset in range(1, future_classes + 1):
                class_date = today + timedelta(days=offset)
                if class_date.weekday() >= 5:
                    continue
                session.add(
                    ClassSchedule(
                        subject_id=subject.id,
                        date=class_date,
                        is_conducted=True,
                    )
                )

        session.commit()

        print("Structured seeding complete: 1000 students with banded attendance and future classes.")


if __name__ == "__main__":
    seed_students()

