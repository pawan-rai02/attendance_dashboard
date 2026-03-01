# Frontend Integration Guide

## Overview

This guide explains the complete frontend integration with the existing FastAPI backend.

## Updated Project Structure

```
attendance_dashboard/
│
├── backend/
│   ├── main.py                 # Updated with static files & templates
│   ├── models.py               # SQLAlchemy models (unchanged)
│   ├── database.py             # Database config (unchanged)
│   ├── schemas.py              # Pydantic schemas (unchanged)
│   ├── routes/                 # API routes (unchanged)
│   │   ├── students.py
│   │   ├── subjects.py
│   │   ├── attendance.py
│   │   └── analytics.py
│   ├── services/               # Business logic (unchanged)
│   ├── utils/                  # Helpers (unchanged)
│   └── templates/              # NEW: Jinja2 HTML templates
│       ├── base.html           # Base template with navbar
│       ├── index.html          # Landing page
│       ├── student.html        # Student dashboard
│       └── dashboard.html      # Class analytics page
│
├── static/                     # NEW: Static assets
│   ├── css/
│   │   └── styles.css          # Custom styles
│   └── js/
│       └── app.js              # Frontend JavaScript
│
├── ml/                         # ML models (unchanged)
├── tests/                      # Tests (unchanged)
├── Dockerfile                  # Updated for static files
├── docker-compose.yml          # Simplified (no separate frontend)
├── requirements.txt            # Updated with Jinja2
└── README.md                   # Documentation
```

---

## File Connections Explained

### 1. Backend (main.py)

**What Changed:**
```python
# Import new modules
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="backend/templates")

# New frontend routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/student")
async def student_dashboard(request: Request):
    return templates.TemplateResponse("student.html", {"request": request})

@app.get("/analytics")
async def class_analytics(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
```

**API Routes Unchanged:**
- All `/api/v1/*` routes remain the same
- Existing functionality preserved

---

### 2. Templates (Jinja2)

**base.html** - Master template:
- Navigation bar with links to all pages
- Footer
- CSS/JS includes via `url_for('static', path='...')`
- Chart.js CDN for visualizations
- Bootstrap 5 CDN for responsive layout

**index.html** - Landing page:
- Hero section with CTAs
- Feature cards
- Live dashboard summary (fetched via JS)
- Defaulters table

**student.html** - Student dashboard:
- Student dropdown selector
- Attendance details container
- Risk assessment display
- Monthly trend chart

**dashboard.html** - Class analytics:
- Subject-wise analytics cards
- Average attendance bar chart
- Top defaulters table

---

### 3. JavaScript (static/js/app.js)

**API Configuration:**
```javascript
const API_BASE_URL = window.location.origin + '/api/v1';
```

**Key Functions:**

| Function | Purpose | API Endpoint |
|----------|---------|--------------|
| `fetchDashboardSummary()` | Get overall stats | `/analytics/dashboard/summary` |
| `fetchStudents()` | Populate dropdown | `/students/?limit=500` |
| `fetchStudentAttendance(id)` | Student details | `/attendance/analytics/student/{id}/complete` |
| `fetchStudentRisk(id)` | Risk assessment | `/analytics/risk/student/{id}` |
| `fetchAllSubjectsAnalytics()` | Class analytics | `/analytics/class/all-subjects` |
| `fetchDefaulters()` | Low attendance list | `/analytics/dashboard/defaulters` |

**Chart Rendering:**
- `renderMonthlyTrendChart()` - Line chart for student trends
- `renderSubjectAttendanceChart()` - Bar chart for subject averages

---

### 4. CSS (static/css/styles.css)

**Custom Variables:**
```css
:root {
    --primary-color: #4f46e5;
    --success-color: #10b981;
    --danger-color: #ef4444;
    --warning-color: #f59e0b;
}
```

**Key Components:**
- `.navbar` - Sticky navigation
- `.stat-card` - Metric display cards
- `.badge` - Status indicators
- `.chart-container` - Chart.js wrappers
- `.loading` - Spinner animation
- `.alert` - Message boxes

---

## How Data Flows

```
User Action → JavaScript → Fetch API → FastAPI Route → Service → Database
                ↓                                              ↓
            DOM Update ← JSON Response ← Service Result ← Query Result
```

### Example: Student Selection

1. User selects student from dropdown
2. `student-select` change event fires
3. `renderStudentDetails(studentId)` called
4. Two parallel API calls:
   - `fetchStudentAttendance(studentId)`
   - `fetchStudentRisk(studentId)`
5. HTML generated with results
6. Chart.js renders monthly trend
7. DOM updated with `innerHTML`

---

## Running the Application

### Development (without Docker)

```bash
# 1. Activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_db
export SEED_DATA=true

# 4. Run the application
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access:**
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Production (with Docker)

```bash
# Build and run
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

**Access:**
- Frontend: http://localhost:8000
- Database: localhost:5432

---

## API Endpoints Reference

All existing API endpoints work unchanged:

### Students
- `GET /api/v1/students/` - List students
- `POST /api/v1/students/` - Create student
- `GET /api/v1/students/{id}` - Get student
- `PUT /api/v1/students/{id}` - Update student
- `DELETE /api/v1/students/{id}` - Delete student

### Attendance
- `GET /api/v1/attendance/student/{id}` - Student attendance
- `GET /api/v1/attendance/analytics/student/{id}/complete` - Full analytics
- `POST /api/v1/attendance/` - Mark attendance

### Analytics
- `GET /api/v1/analytics/dashboard/summary` - Dashboard stats
- `GET /api/v1/analytics/risk/student/{id}` - Risk assessment
- `GET /api/v1/analytics/class/all-subjects` - Class analytics
- `POST /api/v1/analytics/risk/predict` - ML prediction

---

## Customization Guide

### Change Theme Colors

Edit `static/css/styles.css`:
```css
:root {
    --primary-color: #your-color;
    --success-color: #your-color;
    /* ... */
}
```

### Add New Page

1. Create template in `backend/templates/`:
```html
{% extends "base.html" %}

{% block title %}New Page{% endblock %}
{% block page_id %}newpage{% endblock %}

{% block content %}
<!-- Your content -->
{% endblock %}
```

2. Add route in `backend/main.py`:
```python
@app.get("/new-page", response_class=HTMLResponse)
async def new_page(request: Request):
    return templates.TemplateResponse("newpage.html", {"request": request})
```

3. Add JS functions in `static/js/app.js`

### Modify Navigation

Edit `backend/templates/base.html`:
```html
<ul class="navbar-nav">
    <li><a href="/" class="nav-link">🏠 Home</a></li>
    <!-- Add new links here -->
</ul>
```

---

## Troubleshooting

### Static Files Not Loading

**Check:**
```python
# In main.py, verify paths
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
static_dir = project_root / "static"
```

**Test:**
```bash
curl http://localhost:8000/static/css/styles.css
```

### Templates Not Rendering

**Check:**
- Template exists in `backend/templates/`
- Template name matches route
- Jinja2 installed: `pip show jinja2`

### API Calls Failing

**Check browser console for:**
- CORS errors (should be fixed with middleware)
- 404 errors (check API_BASE_URL)
- Network tab for response details

---

## Performance Tips

1. **Enable Gzip Compression:**
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

2. **Cache Static Assets:**
```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
```

3. **Use CDN for Libraries:**
- Bootstrap 5: Already using CDN
- Chart.js: Already using CDN

---

## Security Considerations

1. **Add Authentication** for production
2. **Rate Limiting** on API endpoints
3. **Input Sanitization** in JavaScript
4. **HTTPS** in production
5. **Environment Variables** for sensitive data

---

## Next Steps

1. ✅ Run the application
2. ✅ Test all pages load correctly
3. ✅ Verify API calls work
4. ✅ Customize branding/colors
5. ⬜ Add authentication
6. ⬜ Add more visualizations
7. ⬜ Implement real-time updates with WebSockets
