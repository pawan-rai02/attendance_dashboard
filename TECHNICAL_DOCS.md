# Technical Documentation - College Attendance Analytics Dashboard

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Time Complexity Analysis](#time-complexity-analysis)
3. [Scalability Considerations](#scalability-considerations)
4. [Multi-College SaaS Extension](#multi-college-saas-extension)
5. [Security Best Practices](#security-best-practices)
6. [Performance Optimization](#performance-optimization)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Streamlit     │  │   Swagger UI    │  │  Mobile Apps    │ │
│  │   Dashboard     │  │   /docs         │  │  (Future)       │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      API GATEWAY        │
                    │    (FastAPI + CORS)     │
                    └────────────┬────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
    ┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
    │   Student      │  │   Attendance   │  │   Analytics    │
    │   Service      │  │   Service      │  │   Service      │
    └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      DATA LAYER         │
                    │    (PostgreSQL + ORM)   │
                    └─────────────────────────┘
```

---

## Time Complexity Analysis

### Core Analytics Functions

#### 1. `calculate_overall_attendance(student_id)`

```python
# SQL Query with Index
SELECT COUNT(*), SUM(is_present) 
FROM attendance_records 
WHERE student_id = ?
```

- **Time Complexity**: O(log n)
  - B-Tree index lookup on `student_id`: O(log n)
  - Aggregation over matching rows: O(k) where k << n
- **Space Complexity**: O(1)
  - Single aggregation result returned

#### 2. `calculate_subject_wise_attendance(student_id)`

```python
# SQL with JOIN and GROUP BY
SELECT s.id, s.subject_code, COUNT(*), SUM(ar.is_present)
FROM subjects s
JOIN attendance_records ar ON ar.subject_id = s.id
WHERE ar.student_id = ?
GROUP BY s.id
```

- **Time Complexity**: O(m × log n)
  - m = number of subjects
  - Index lookup for each subject's records
- **Space Complexity**: O(m)
  - Result list proportional to subjects

#### 3. `calculate_monthly_trend(student_id, months=6)`

```python
# SQL with date extraction
SELECT EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date),
       COUNT(*), SUM(is_present)
FROM attendance_records
WHERE student_id = ?
GROUP BY year, month
ORDER BY year DESC, month DESC
LIMIT 6
```

- **Time Complexity**: O(n)
  - Full scan of student's records
  - Could be O(log n) with composite index (student_id, date)
- **Space Complexity**: O(k)
  - k = number of months (bounded by parameter)

#### 4. `get_class_analytics(subject_id)`

```python
# Aggregation per student for a subject
SELECT student_id, COUNT(*), SUM(is_present)
FROM attendance_records
WHERE subject_id = ?
GROUP BY student_id
```

- **Time Complexity**: O(s × log a)
  - s = number of students
  - a = attendance records per student
- **Space Complexity**: O(s)
  - One row per student in result

#### 5. `calculate_risk_for_student(student_id, subject_id)`

```python
# Mathematical calculation
# x >= 0.75 * (total + remaining) - present
# If x > remaining: IMPOSSIBLE
```

- **Time Complexity**: O(log n)
  - Single query for attendance stats
- **Space Complexity**: O(1)
  - Fixed number of calculations

### ML Prediction Functions

#### 6. `MLPredictor.predict(features)`

```python
# Sigmoid(w·x + b)
z = sum(w_i * x_i) + b
probability = 1 / (1 + exp(-z))
```

- **Time Complexity**: O(m)
  - m = number of features (fixed at 5)
  - Effectively O(1) for constant features
- **Space Complexity**: O(1)
  - Weights stored in memory

#### 7. `MLPredictor.fit(X, y)`

```python
# Gradient descent for n_iterations
for i in range(n_iterations):
    predictions = sigmoid(X @ weights + bias)
    gradients = X.T @ (predictions - y) / n_samples
    weights -= learning_rate * gradients
```

- **Time Complexity**: O(i × n × m)
  - i = iterations
  - n = samples
  - m = features
- **Space Complexity**: O(n × m)
  - Storage for training data

---

## Scalability Considerations

### Current Architecture Limits

| Component | Current Capacity | Bottleneck |
|-----------|-----------------|------------|
| Database | ~100K records | Single PostgreSQL instance |
| API | ~100 req/sec | Single FastAPI instance |
| Frontend | ~50 concurrent users | Streamlit's single-threaded nature |
| ML Model | Real-time prediction | Model loading in memory |

### Scaling Strategies

#### 1. Database Scaling

**Vertical Scaling:**
```sql
-- Increase PostgreSQL resources
-- shared_buffers = 4GB
-- work_mem = 256MB
-- effective_cache_size = 12GB
```

**Horizontal Scaling:**
```sql
-- Table partitioning by date
CREATE TABLE attendance_2024_q1 PARTITION OF attendance_records
FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE attendance_2024_q2 PARTITION OF attendance_records
FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
```

**Read Replicas:**
```python
# Route read queries to replicas
class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None):
        if self._flushing:
            return master_engine
        else:
            return random.choice(replica_engines)
```

#### 2. API Scaling

**Horizontal Scaling with Load Balancer:**
```yaml
# docker-compose for multiple API instances
services:
  api-1:
    <<: *api-service
    ports:
      - "8001:8000"
  
  api-2:
    <<: *api-service
    ports:
      - "8002:8000"
  
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
```

**Async Processing:**
```python
from fastapi import BackgroundTasks

@app.post("/attendance/bulk")
async def bulk_attendance(
    records: AttendanceRecordBulk,
    background_tasks: BackgroundTasks
):
    # Return immediately, process in background
    background_tasks.add_task(process_bulk_attendance, records)
    return {"status": "processing", "count": len(records.records)}
```

#### 3. Caching Layer

**Redis Integration:**
```python
from redis import Redis
from functools import wraps

cache = Redis(host='redis', port=6379, db=0)

def cache_result(expiry: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            cached = cache.get(key)
            if cached:
                return json.loads(cached)
            result = func(*args, **kwargs)
            cache.setex(key, expiry, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiry=60)
def get_dashboard_summary():
    # Expensive database query
    ...
```

#### 4. Frontend Scaling

**Streamlit Alternatives for High Traffic:**
- React + FastAPI for production
- Next.js for SSR capabilities
- Deploy multiple Streamlit instances behind load balancer

---

## Multi-College SaaS Extension

### Database Schema Changes

```python
class College(Base):
    __tablename__ = "colleges"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    subdomain = Column(String(50), unique=True, nullable=False)
    api_key = Column(String(64), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    students = relationship("Student", back_populates="college")
    subjects = relationship("Subject", back_populates="college")


# Add college_id to existing models
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False)
    # ... existing fields ...
    
    college = relationship("College", back_populates="students")
```

### Tenant Resolution Middleware

```python
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def resolve_tenant(
    request: Request,
    api_key: str = Depends(api_key_header)
):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    college = db.query(College).filter(
        College.api_key == api_key,
        College.is_active == True
    ).first()
    
    if not college:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    request.state.college = college
    request.state.college_id = college.id
```

### Row-Level Security (PostgreSQL)

```sql
-- Enable RLS
ALTER TABLE students ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation
CREATE POLICY college_isolation ON students
USING (college_id = current_setting('app.current_college_id')::int);

-- Set context in application
SET app.current_college_id = 1;
```

### Subscription Tiers

```python
class SubscriptionTier(Enum):
    FREE = "free"           # Up to 100 students
    BASIC = "basic"         # Up to 500 students
    PRO = "pro"             # Up to 2000 students
    ENTERPRISE = "enterprise"  # Unlimited

class College(Base):
    # ... existing fields ...
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires = Column(DateTime)
```

---

## Security Best Practices

### 1. Authentication & Authorization

```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401)
    return user
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/students/{student_id}")
@limiter.limit("100/minute")
async def get_student(request: Request, student_id: int):
    ...
```

### 3. Input Sanitization

```python
from pydantic import validator
import re

class StudentCreate(BaseModel):
    name: str
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s\-\.]+$', v):
            raise ValueError('Invalid characters in name')
        if len(v) > 100:
            raise ValueError('Name too long')
        return v.strip()
```

### 4. SQL Injection Prevention

```python
# ✅ SAFE - Using ORM
students = db.query(Student).filter(Student.name == name).all()

# ❌ UNSAFE - Raw SQL with string formatting
students = db.execute(f"SELECT * FROM students WHERE name = '{name}'")
```

---

## Performance Optimization

### 1. Database Query Optimization

```python
# Use eager loading to avoid N+1 queries
from sqlalchemy.orm import joinedload

students = db.query(Student).options(
    joinedload(Student.attendance_records)
).all()

# Use selectinload for collections
from sqlalchemy.orm import selectinload

students = db.query(Student).options(
    selectinload(Student.attendance_records)
).all()
```

### 2. Batch Operations

```python
# ❌ Slow - Individual inserts
for record in records:
    db.add(AttendanceRecord(**record))
db.commit()

# ✅ Fast - Bulk insert
db.bulk_insert_mappings(AttendanceRecord, records)
db.commit()
```

### 3. Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to keep
    max_overflow=40,       # Additional connections when needed
    pool_pre_ping=True,    # Health check before using connection
    pool_recycle=3600      # Recycle connections after 1 hour
)
```

### 4. Async Operations

```python
from fastapi import FastAPI
from databases import Database

app = FastAPI()
database = Database(DATABASE_URL)

@app.get("/students")
async def get_students():
    query = "SELECT * FROM students"
    return await database.fetch_all(query)
```

---

## Monitoring & Observability

### 1. Health Checks

```python
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Database health
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 2. Metrics Collection

```python
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Access metrics at /metrics
```

### 3. Structured Logging

```python
import structlog

logger = structlog.get_logger()

@app.post("/students/")
async def create_student(student: StudentCreate):
    logger.info("creating_student", roll_number=student.roll_number)
    # ... logic ...
    logger.info("student_created", student_id=student.id)
```

---

## Conclusion

This technical documentation provides a comprehensive guide for:
- Understanding the time and space complexity of key operations
- Scaling the application for increased load
- Extending to a multi-tenant SaaS model
- Implementing security best practices
- Optimizing performance

For questions or contributions, please refer to the main README.md.
