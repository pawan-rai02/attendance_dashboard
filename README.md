# 🎓 College Attendance Analytics Dashboard

An easy-to-use **attendance and analytics website** for colleges and schools.  
It helps **teachers, department heads, and students** quickly see:

- Which students are **safe**, **at risk**, or **in serious danger** of falling below 75% attendance.
- Subject-wise and class-wise **attendance trends**.
- Clear, visual dashboards instead of manual Excel sheets.

You do **not** need to know programming to use the dashboard once it is set up.

![Dashboard Preview](docs/dashboard-preview.png)

---

## 1. Who this project is for

- **Principals / Management**
  - See overall attendance health of the institution.
  - Quickly identify defaulter trends across departments.
- **Heads of Department / Class Coordinators**
  - Monitor each class and subject.
  - Find students who are close to shortage and act early.
- **Teachers**
  - Track subject-wise attendance.
  - See which students regularly miss a particular subject.
- **Students**
  - Check your own attendance percentage.
  - Understand how many more classes you need to attend to be safe.

---

## 2. How the dashboard works (simple explanation)

- **Attendance rules**
  - Each subject has a required number of classes (for example, 60 classes).
  - A student is expected to attend **at least 75%** of classes.
  - The system uses the formula:
    - **Attendance % = (Classes Present ÷ Total Classes Conducted) × 100**

- **Risk levels**
  - **Safe**: Attendance is comfortably above 75%.
  - **Borderline / At Risk**: Attendance is near 75%; a few missed classes can cause a shortage.
  - **Critical**: Attendance is already too low; even if the student attends all future classes, it may be hard or impossible to reach 75%.

- **Automatic analytics**
  - The system reads attendance data from the database.
  - It calculates:
    - Overall attendance for each student.
    - Subject-wise attendance.
    - Class / department-level statistics.
    - Lists of defaulters (below 75%).
  - Results are shown on clean, visual dashboards in your browser.

---

## 3. How to open and use the website

- **If the dashboard is already hosted for you**  
  Ask your IT team or developer for the link (for example, `http://localhost:8000` or a college domain), open it in a browser, and then use the pages described below.

- **If you want to run it on your own machine (development / Windows setup)**  
  Please read `RUN_INSTRUCTIONS.md`. That file is the **single source of truth** for all installation and run commands (virtual environment, `start.bat`, manual `uvicorn`, database options, and troubleshooting).

---

## 4. What you see on each page

### 4.1 Landing Page (`/`)

This is the **home page** of the dashboard. It typically shows:

- **Key summary cards**
  - Total number of students.
  - Average attendance across the institution.
  - Number / percentage of defaulters (below 75%).
- **Defaulters table**
  - List of at-risk students with:
    - Name and roll number.
    - Department and semester.
    - Current attendance percentage.
- **Navigation links**
  - Buttons or menu links to:
    - Student Dashboard
    - Class Analytics
    - API Documentation (for technical users)

Use this page to get a **quick health snapshot** of your college.

### 4.2 Student Dashboard Page (`/student`)

This page is focused on **one student at a time**.

1. **Select a student**
   - At the top, you will see a **dropdown list** of students.
   - Choose a student by name or roll number.
2. After selection, you will see:
   - **Overall attendance gauge**
     - A big number (for example, `78%`) with a colored indicator:
       - Green: Safe.
       - Yellow/Orange: At risk.
       - Red: Critical.
   - **Subject-wise table**
     - Each row shows:
       - Subject name and code.
       - Classes conducted.
       - Classes attended.
       - Attendance percentage for that subject.
   - **Monthly trend chart**
     - A line chart showing how the student’s attendance changed over recent months.
   - **“Classes remaining vs. needed” information**
     - How many classes are left in the semester.
     - Minimum number of classes the student must attend to stay at or reach 75%.

**How to use this page**

- For **mentors or advisors**:
  - Sit with the student and open their dashboard.
  - Explain which subjects are causing risk and what they need to do.
- For **students**:
  - Check your own attendance regularly.
  - Plan your attendance so you do not become a defaulter at the end of the term.

### 4.3 Class Analytics Page (`/analytics`)

This page is focused on **subjects and classes**, not just individual students.

You will see:

- **Subject cards**
  - For each subject:
    - Average attendance percentage.
    - Number of students at risk in that subject.
- **Charts**
  - Bar charts or other visuals to compare subjects.
  - Helps you quickly spot:
    - Which subject has the weakest overall attendance.
    - Which classes need intervention (e.g., more engagement, reminders).
- **Top defaulters by subject**
  - A table of students who are repeatedly short in specific subjects.

**How to use this page**

- For **Heads of Department**:
  - Use this page in meetings to discuss overall class discipline.
  - See whether some subjects are consistently under-attended.
- For **teachers**:
  - Compare your subject with others.
  - Decide if you need to adjust schedule, communication, or reminders.

---

## 5. Sample data for testing and demos

This project comes with **automatic sample data** so you can explore the dashboard without entering real student data first.

- When the application starts with sample seeding enabled:
  - It creates **many realistic-looking students** across departments.
  - It adds several **subjects** (e.g., Data Structures, Database Management).
  - It generates **attendance records over ~90 days**, with different patterns:
    - Some students with very good attendance.
    - Some with average attendance.
    - Some defaulters with very low attendance.
- This results in **thousands of attendance rows**, which makes the charts and analytics look realistic.

> Names and email addresses in this demo data are **fictional** and safe to use for testing or demonstrations.

---

## 6. Glossary – plain language explanations

- **Attendance percentage**  
  How regularly a student has attended classes, expressed as a percentage.  
  Example: 45 classes present out of 60 ⇒ 75%.

- **Defaulter**  
  A student whose attendance is **below the minimum required percentage** (often 75%).

- **At-risk student**  
  A student who is **close to becoming a defaulter**. Their attendance is near the minimum, so a few more absences can push them below the limit.

- **Analytics**  
  Simple summaries and charts that help you see patterns:
  - Which subjects are being missed.
  - Which students regularly skip classes.

- **Dashboard**  
  A web page that shows important information in one place using charts, cards, and tables.

- **API (for developers)**  
  A technical interface that allows other software (like mobile apps or other websites) to talk to this system programmatically.

---

## 7. Typical usage scenarios

- **Before internal tests or university exams**
  - Use the **Class Analytics** page to identify all students below 75% and send them warnings or counseling reminders.

- **Monthly review meetings**
  - Project the dashboard on a screen.
  - Use the **Landing Page** and **Class Analytics** page to discuss department-wise trends.

- **Student counseling sessions**
  - Open the **Student Dashboard** for a particular student.
  - Show them exact numbers and how many more classes they must attend to become safe.

---

## 8. For technical users and developers

The sections above were written for **non-technical users**.  
If you are a **developer** or **IT engineer** who wants to work with the codebase, this section is for you.

### 8.1 High-level technical overview

- **Backend**
  - Built with **FastAPI** (Python).
  - Provides REST-style APIs under `/api/v1`.
  - Serves HTML pages using **Jinja2 templates**.
- **Database**
  - By default on this machine, development runs on **SQLite** (`backend/attendance.db`) so you do *not* need PostgreSQL just to try it.
  - In production, you can point it to **PostgreSQL** using the `DATABASE_URL` environment variable.
- **Frontend**
  - HTML templates with **Bootstrap 5** and **Chart.js**.
  - Static assets live under `static/css` and `static/js`.
- **ML (optional)**
  - Logistic Regression model (scikit-learn) to estimate shortage risk.

### 8.2 Important folders (developer view)

```text
attendance_dashboard/
│
├── backend/                 # FastAPI app (Python)
│   ├── main.py              # App factory, routes, templates, seeding
│   ├── database.py          # DB configuration (SQLite / PostgreSQL)
│   ├── models.py            # SQLAlchemy ORM models
│   ├── routes/              # API route modules
│   ├── services/            # Business logic and analytics
│   ├── utils/               # Helpers and utilities
│   └── templates/           # HTML templates (Jinja2)
│
├── static/                  # CSS and JS for the UI
├── ml/                      # ML model training and code (optional)
├── tests/                   # Automated tests
├── RUN_INSTRUCTIONS.md      # Step-by-step run guide (Windows-focused)
├── TECHNICAL_DOCS.md        # Deep-dive architecture, scaling, security
└── FRONTEND_INTEGRATION.md  # Detailed frontend wiring and customization
```

### 8.3 Running locally (pointer only)

- For **all setup and run commands** (virtual environment, `start.bat`, manual `uvicorn`, SQLite vs PostgreSQL), see `RUN_INSTRUCTIONS.md`.  
- For deep technical topics such as **time complexity, scaling, security, SaaS multi-tenancy**, see `TECHNICAL_DOCS.md`.

---

## 9. License, contributions, and contact

- **License**: MIT License (see the `LICENSE` file if present).
- **Contributions**:
  - Fork the repository.
  - Create a feature branch.
  - Submit a pull request with a clear description.
- **Contact / Support**:
  - Open an issue in the repository if you find bugs or have feature requests.

---

*Built for educational institutions that want clear, data-driven attendance decisions without wrestling with spreadsheets.*
