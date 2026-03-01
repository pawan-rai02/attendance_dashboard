/**
 * College Attendance Analytics Dashboard
 * Main JavaScript Application
 * 
 * Handles all API calls and DOM manipulation
 */

// ============================================
// API Configuration
// ============================================
const API_BASE_URL = window.location.origin + '/api/v1';

// ============================================
// Utility Functions
// ============================================

/**
 * Show loading state in an element
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <span class="loading-text">Loading...</span>
            </div>
        `;
    }
}

/**
 * Show error message
 */
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger">
                <span>⚠️</span>
                <span>${message}</span>
            </div>
        `;
    }
}

/**
 * Format percentage with color coding
 */
function formatPercentage(value) {
    const numValue = parseFloat(value);
    let className = 'text-success';
    if (numValue < 50) className = 'text-danger';
    else if (numValue < 60) className = 'text-warning';
    else if (numValue < 75) className = 'text-danger';
    
    return `<span class="${className}"><strong>${numValue.toFixed(1)}%</strong></span>`;
}

/**
 * Get attendance status badge
 */
function getAttendanceBadge(percentage) {
    const numValue = parseFloat(percentage);
    if (numValue >= 90) {
        return '<span class="badge badge-success">✓ Excellent</span>';
    } else if (numValue >= 75) {
        return '<span class="badge badge-success">✓ Good</span>';
    } else if (numValue >= 60) {
        return '<span class="badge badge-warning">⚠ Average</span>';
    } else if (numValue >= 50) {
        return '<span class="badge badge-danger">⚠ Poor</span>';
    } else {
        return '<span class="badge badge-danger">⚠ Critical</span>';
    }
}

/**
 * Get risk status badge
 */
function getRiskBadge(riskScore, isImpossible) {
    if (isImpossible) {
        return '<span class="badge badge-danger">🚨 Impossible</span>';
    } else if (riskScore >= 70) {
        return '<span class="badge badge-danger">🔴 High Risk</span>';
    } else if (riskScore >= 40) {
        return '<span class="badge badge-warning">🟡 Medium Risk</span>';
    } else {
        return '<span class="badge badge-success">🟢 Low Risk</span>';
    }
}

// ============================================
// API Functions
// ============================================

/**
 * Fetch dashboard summary
 */
async function fetchDashboardSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/dashboard/summary`);
        if (!response.ok) throw new Error('Failed to fetch dashboard summary');
        return await response.json();
    } catch (error) {
        console.error('Error fetching dashboard summary:', error);
        throw error;
    }
}

/**
 * Fetch all students
 */
async function fetchStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/students/?limit=500`);
        if (!response.ok) throw new Error('Failed to fetch students');
        const data = await response.json();
        return data.items || [];
    } catch (error) {
        console.error('Error fetching students:', error);
        throw error;
    }
}

/**
 * Fetch all subjects
 */
async function fetchSubjects() {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/?limit=100`);
        if (!response.ok) throw new Error('Failed to fetch subjects');
        const data = await response.json();
        return data.items || [];
    } catch (error) {
        console.error('Error fetching subjects:', error);
        throw error;
    }
}

/**
 * Fetch student attendance trend
 */
async function fetchStudentAttendance(studentId) {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/analytics/student/${studentId}/complete`);
        if (!response.ok) throw new Error('Failed to fetch student attendance');
        return await response.json();
    } catch (error) {
        console.error('Error fetching student attendance:', error);
        throw error;
    }
}

/**
 * Fetch student risk assessment
 */
async function fetchStudentRisk(studentId, subjectId = null) {
    try {
        let url = `${API_BASE_URL}/analytics/risk/student/${studentId}`;
        if (subjectId) {
            url += `?subject_id=${subjectId}`;
        }
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch risk assessment');
        return await response.json();
    } catch (error) {
        console.error('Error fetching risk assessment:', error);
        throw error;
    }
}

/**
 * Fetch all at-risk students
 */
async function fetchAtRiskStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/risk/all-at-risk`);
        if (!response.ok) throw new Error('Failed to fetch at-risk students');
        return await response.json();
    } catch (error) {
        console.error('Error fetching at-risk students:', error);
        throw error;
    }
}

/**
 * Fetch class analytics for a subject
 */
async function fetchClassAnalytics(subjectId) {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/class/subject/${subjectId}`);
        if (!response.ok) throw new Error('Failed to fetch class analytics');
        return await response.json();
    } catch (error) {
        console.error('Error fetching class analytics:', error);
        throw error;
    }
}

/**
 * Fetch all subjects analytics
 */
async function fetchAllSubjectsAnalytics() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/class/all-subjects`);
        if (!response.ok) throw new Error('Failed to fetch subjects analytics');
        return await response.json();
    } catch (error) {
        console.error('Error fetching subjects analytics:', error);
        throw error;
    }
}

/**
 * Fetch defaulters list
 */
async function fetchDefaulters(limit = 50) {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/dashboard/defaulters?limit=${limit}`);
        if (!response.ok) throw new Error('Failed to fetch defaulters');
        return await response.json();
    } catch (error) {
        console.error('Error fetching defaulters:', error);
        throw error;
    }
}

// ============================================
// Render Functions - Dashboard
// ============================================

/**
 * Render dashboard summary cards
 */
async function renderDashboardSummary() {
    showLoading('stats-container');
    
    try {
        const summary = await fetchDashboardSummary();
        
        const html = `
            <div class="stat-card">
                <div class="stat-card-icon primary">👨‍🎓</div>
                <div class="stat-card-value">${summary.total_students || 0}</div>
                <div class="stat-card-label">Total Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-icon success">📚</div>
                <div class="stat-card-value">${summary.total_subjects || 0}</div>
                <div class="stat-card-label">Total Subjects</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-icon warning">📊</div>
                <div class="stat-card-value">${(summary.overall_attendance_avg || 0).toFixed(1)}%</div>
                <div class="stat-card-label">Average Attendance</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-icon danger">⚠️</div>
                <div class="stat-card-value">${summary.total_defaulters || 0}</div>
                <div class="stat-card-label">Defaulters</div>
            </div>
        `;
        
        document.getElementById('stats-container').innerHTML = html;
    } catch (error) {
        showError('stats-container', 'Failed to load dashboard summary. Please refresh the page.');
    }
}

/**
 * Render defaulters table
 */
async function renderDefaultersTable() {
    showLoading('defaulters-container');
    
    try {
        const defaulters = await fetchDefaulters(20);
        
        if (!defaulters || defaulters.length === 0) {
            document.getElementById('defaulters-container').innerHTML = `
                <div class="alert alert-success">
                    <span>🎉</span>
                    <span>No defaulters! All students have good attendance.</span>
                </div>
            `;
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Roll Number</th>
                            <th>Name</th>
                            <th>Department</th>
                            <th>Attendance</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        defaulters.forEach(student => {
            html += `
                <tr>
                    <td><strong>${student.roll_number}</strong></td>
                    <td>${student.name}</td>
                    <td>${student.department}</td>
                    <td>${formatPercentage(student.attendance_percentage)}</td>
                    <td>${getAttendanceBadge(student.attendance_percentage)}</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        document.getElementById('defaulters-container').innerHTML = html;
    } catch (error) {
        showError('defaulters-container', 'Failed to load defaulters list.');
    }
}

// ============================================
// Render Functions - Student Dashboard
// ============================================

/**
 * Populate student dropdown
 */
async function populateStudentDropdown() {
    try {
        const students = await fetchStudents();
        const select = document.getElementById('student-select');
        
        if (!select) return;
        
        select.innerHTML = '<option value="">-- Select a Student --</option>';
        
        students.forEach(student => {
            select.innerHTML += `
                <option value="${student.id}">${student.roll_number} - ${student.name}</option>
            `;
        });
    } catch (error) {
        console.error('Failed to populate student dropdown:', error);
    }
}

/**
 * Render student attendance details
 */
async function renderStudentDetails(studentId) {
    if (!studentId) {
        document.getElementById('student-attendance-content').innerHTML = `
            <div class="alert alert-info">
                <span>ℹ️</span>
                <span>Please select a student to view their attendance details.</span>
            </div>
        `;
        return;
    }
    
    showLoading('student-attendance-content');
    
    try {
        const [attendanceData, riskData] = await Promise.all([
            fetchStudentAttendance(studentId),
            fetchStudentRisk(studentId)
        ]);
        
        // Overall attendance gauge
        const overallPct = attendanceData.overall_attendance || 0;
        const riskScore = riskData.risk_score || 0;
        
        let html = `
            <!-- Risk Alert -->
            <div class="alert ${riskData.is_impossible ? 'alert-danger' : riskData.is_at_risk ? 'alert-warning' : 'alert-success'} mb-3">
                <span>${riskData.is_impossible ? '🚨' : riskData.is_at_risk ? '⚠️' : '✅'}</span>
                <span><strong>${riskData.is_impossible ? 'CRITICAL' : riskData.is_at_risk ? 'WARNING' : 'GOOD'}</strong>: ${riskData.recommendation || 'Student is on track.'}</span>
            </div>
            
            <!-- Stats Row -->
            <div class="stats-grid mb-4">
                <div class="stat-card">
                    <div class="stat-card-icon primary">📊</div>
                    <div class="stat-card-value">${overallPct.toFixed(1)}%</div>
                    <div class="stat-card-label">Overall Attendance</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon ${riskData.is_at_risk ? 'danger' : 'success'}">⚠️</div>
                    <div class="stat-card-value">${riskScore.toFixed(0)}</div>
                    <div class="stat-card-label">Risk Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon warning">📅</div>
                    <div class="stat-card-value">${riskData.classes_remaining || 0}</div>
                    <div class="stat-card-label">Classes Remaining</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon success">✓</div>
                    <div class="stat-card-value">${riskData.min_classes_needed || 0}</div>
                    <div class="stat-card-label">Classes Needed</div>
                </div>
            </div>
            
            <!-- Risk Status -->
            <div class="card mb-4">
                <div class="card-header">
                    <h3 class="card-title">Risk Assessment</h3>
                </div>
                <div class="d-flex align-items-center gap-3">
                    ${getRiskBadge(riskScore, riskData.is_impossible)}
                    <span class="text-muted">Current: ${riskData.current_attendance_pct?.toFixed(1) || 0}% | Target: 75%</span>
                </div>
            </div>
            
            <!-- Subject-wise Table -->
            <div class="card mb-4">
                <div class="card-header">
                    <h3 class="card-title">Subject-wise Attendance</h3>
                </div>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Subject Code</th>
                                <th>Subject Name</th>
                                <th>Classes</th>
                                <th>Present</th>
                                <th>Attendance</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        if (attendanceData.subject_wise && attendanceData.subject_wise.length > 0) {
            attendanceData.subject_wise.forEach(subject => {
                html += `
                    <tr>
                        <td><strong>${subject.subject_code}</strong></td>
                        <td>${subject.subject_name}</td>
                        <td>${subject.total_classes}</td>
                        <td>${subject.classes_present}</td>
                        <td>${formatPercentage(subject.attendance_percentage)}</td>
                        <td>${getAttendanceBadge(subject.attendance_percentage)}</td>
                    </tr>
                `;
            });
        } else {
            html += `<tr><td colspan="6" class="text-center text-muted">No subject data available</td></tr>`;
        }
        
        html += `
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Monthly Trend Chart -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Monthly Attendance Trend</h3>
                </div>
                <div class="chart-container">
                    <canvas id="monthlyTrendChart"></canvas>
                </div>
            </div>
        `;
        
        document.getElementById('student-attendance-content').innerHTML = html;
        
        // Render monthly trend chart
        if (attendanceData.monthly_trend && attendanceData.monthly_trend.length > 0) {
            renderMonthlyTrendChart(attendanceData.monthly_trend);
        }
        
    } catch (error) {
        showError('student-attendance-content', 'Failed to load student attendance details.');
        console.error(error);
    }
}

/**
 * Render monthly trend chart using Chart.js
 */
let monthlyTrendChartInstance = null;

function renderMonthlyTrendChart(monthlyData) {
    const ctx = document.getElementById('monthlyTrendChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (monthlyTrendChartInstance) {
        monthlyTrendChartInstance.destroy();
    }
    
    const labels = monthlyData.map(d => d.month);
    const data = monthlyData.map(d => d.attendance_percentage);
    
    monthlyTrendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Attendance %',
                data: data,
                borderColor: '#4f46e5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: value => value + '%'
                    }
                }
            }
        }
    });
}

// ============================================
// Render Functions - Class Analytics
// ============================================

/**
 * Render class analytics page
 */
async function renderClassAnalytics() {
    showLoading('class-analytics-content');
    
    try {
        const [subjectsAnalytics, defaulters] = await Promise.all([
            fetchAllSubjectsAnalytics(),
            fetchDefaulters(10)
        ]);
        
        let html = `
            <!-- Subject Analytics Cards -->
            <div class="stats-grid mb-4">
        `;
        
        if (subjectsAnalytics && subjectsAnalytics.length > 0) {
            subjectsAnalytics.forEach(subject => {
                const avgAtt = subject.average_attendance || 0;
                const atRisk = subject.students_at_risk || 0;
                const totalStudents = subject.total_students || 0;
                
                html += `
                    <div class="card">
                        <div class="card-header">
                            <h4 class="card-title mb-0">${subject.subject_code}</h4>
                            <span class="badge ${avgAtt >= 75 ? 'badge-success' : 'badge-danger'}">
                                ${avgAtt.toFixed(1)}%
                            </span>
                        </div>
                        <p class="text-muted mb-2">${subject.subject_name}</p>
                        <div class="d-flex justify-content-between mb-2">
                            <span class="text-muted">Students:</span>
                            <strong>${totalStudents}</strong>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span class="text-muted">At Risk:</span>
                            <strong class="${atRisk > totalStudents/2 ? 'text-danger' : 'text-success'}">${atRisk}</strong>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span class="text-muted">Defaulter %:</span>
                            <strong class="${subject.defaulter_percentage >= 50 ? 'text-danger' : 'text-success'}">${subject.defaulter_percentage.toFixed(1)}%</strong>
                        </div>
                    </div>
                `;
            });
        } else {
            html += `<div class="alert alert-info w-100">No subject analytics data available.</div>`;
        }
        
        html += `
            </div>
            
            <!-- Average Attendance Chart -->
            <div class="card mb-4">
                <div class="card-header">
                    <h3 class="card-title">Average Attendance by Subject</h3>
                </div>
                <div class="chart-container large">
                    <canvas id="subjectAttendanceChart"></canvas>
                </div>
            </div>
            
            <!-- Top Defaulters -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Students Requiring Attention</h3>
                </div>
        `;
        
        if (defaulters && defaulters.length > 0) {
            html += `
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Roll Number</th>
                                <th>Name</th>
                                <th>Department</th>
                                <th>Attendance</th>
                                <th>Risk Level</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            defaulters.forEach(student => {
                const attPct = student.attendance_percentage || 0;
                let riskLevel = 'Low';
                let riskClass = 'badge-success';
                if (attPct < 50) {
                    riskLevel = 'Critical';
                    riskClass = 'badge-danger';
                } else if (attPct < 60) {
                    riskLevel = 'High';
                    riskClass = 'badge-danger';
                } else if (attPct < 75) {
                    riskLevel = 'Medium';
                    riskClass = 'badge-warning';
                }
                
                html += `
                    <tr>
                        <td><strong>${student.roll_number}</strong></td>
                        <td>${student.name}</td>
                        <td>${student.department}</td>
                        <td>${formatPercentage(attPct)}</td>
                        <td><span class="badge ${riskClass}">${riskLevel}</span></td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            html += `
                <div class="alert alert-success">
                    <span>🎉</span>
                    <span>No defaulters! All students have good attendance.</span>
                </div>
            `;
        }
        
        html += `</div>`;
        
        document.getElementById('class-analytics-content').innerHTML = html;
        
        // Render subject attendance chart
        if (subjectsAnalytics && subjectsAnalytics.length > 0) {
            renderSubjectAttendanceChart(subjectsAnalytics);
        }
        
    } catch (error) {
        showError('class-analytics-content', 'Failed to load class analytics.');
        console.error(error);
    }
}

/**
 * Render subject attendance bar chart
 */
let subjectAttendanceChartInstance = null;

function renderSubjectAttendanceChart(subjectsData) {
    const ctx = document.getElementById('subjectAttendanceChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (subjectAttendanceChartInstance) {
        subjectAttendanceChartInstance.destroy();
    }
    
    const labels = subjectsData.map(s => s.subject_code);
    const data = subjectsData.map(s => s.average_attendance);
    const backgroundColors = data.map(att => att >= 75 ? '#10b981' : att >= 60 ? '#f59e0b' : '#ef4444');
    
    subjectAttendanceChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Attendance %',
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 0,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: value => value + '%'
                    }
                }
            }
        }
    });
}

// ============================================
// Page Initialization
// ============================================

/**
 * Initialize landing page
 */
function initLandingPage() {
    renderDashboardSummary();
    renderDefaultersTable();
}

/**
 * Initialize student dashboard page
 */
function initStudentDashboard() {
    populateStudentDropdown();
    
    const studentSelect = document.getElementById('student-select');
    if (studentSelect) {
        studentSelect.addEventListener('change', (e) => {
            renderStudentDetails(e.target.value);
        });
    }
}

/**
 * Initialize class analytics page
 */
function initClassAnalytics() {
    renderClassAnalytics();
}

// ============================================
// DOM Ready
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Check which page we're on and initialize accordingly
    const pageId = document.body.getAttribute('data-page');
    
    switch (pageId) {
        case 'landing':
            initLandingPage();
            break;
        case 'student':
            initStudentDashboard();
            break;
        case 'analytics':
            initClassAnalytics();
            break;
    }
});
