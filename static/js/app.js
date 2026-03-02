/**
 * Attendance AI Dashboard
 * Premium Dark Theme - JavaScript Application
 * 
 * Handles API calls, DOM manipulation, and smooth animations
 */

// ============================================
// API Configuration
// ============================================
const API_BASE_URL = window.location.origin + '/api/v1';

// ============================================
// Cursor Glow Effect
// ============================================
function initCursorGlow() {
    const cursorGlow = document.getElementById('cursor-glow');
    if (!cursorGlow) return;

    let mouseX = 0, mouseY = 0;
    let glowX = 0, glowY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animate() {
        // Smooth follow
        glowX += (mouseX - glowX) * 0.1;
        glowY += (mouseY - glowY) * 0.1;

        cursorGlow.style.left = glowX + 'px';
        cursorGlow.style.top = glowY + 'px';

        requestAnimationFrame(animate);
    }

    animate();
}

// ============================================
// Particle System
// ============================================
function initParticles() {
    const container = document.getElementById('particles');
    if (!container) return;

    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        createParticle(container);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';

    // Random properties
    const size = Math.random() * 4 + 2;
    const left = Math.random() * 100;
    const delay = Math.random() * 15;
    const duration = Math.random() * 10 + 10;
    const colors = ['#a855f7', '#3b82f6', '#06b6d4'];
    const color = colors[Math.floor(Math.random() * colors.length)];

    particle.style.cssText = `
        width: ${size}px;
        height: ${size}px;
        left: ${left}%;
        animation-delay: ${delay}s;
        animation-duration: ${duration}s;
        background: ${color};
        box-shadow: 0 0 ${size * 3}px ${color};
    `;

    container.appendChild(particle);

    // Remove and recreate after animation
    setTimeout(() => {
        particle.remove();
        createParticle(container);
    }, (duration + delay) * 1000);
}

// ============================================
// Utility Functions
// ============================================

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <span class="loading-text">Loading...</span>
            </div>
        `;
    }
}

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

function formatPercentage(value) {
    const numValue = parseFloat(value);
    let className = 'text-success';
    if (numValue < 50) className = 'text-danger';
    else if (numValue < 60) className = 'text-warning';
    else if (numValue < 75) className = 'text-danger';

    return `<span class="${className}"><strong>${numValue.toFixed(1)}%</strong></span>`;
}

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
// Render Functions - Dashboard (Landing)
// ============================================

async function renderDashboardSummary() {
    showLoading('stats-container');

    try {
        const summary = await fetchDashboardSummary();

        const html = `
            <div class="stat-card animate-fade-in-up">
                <div class="stat-card-icon primary">👨‍🎓</div>
                <div class="stat-card-value">${summary.total_students || 0}</div>
                <div class="stat-card-label">Total Students</div>
            </div>
            <div class="stat-card animate-fade-in-up stagger-1">
                <div class="stat-card-icon success">📚</div>
                <div class="stat-card-value">${summary.total_subjects || 0}</div>
                <div class="stat-card-label">Total Subjects</div>
            </div>
            <div class="stat-card animate-fade-in-up stagger-2">
                <div class="stat-card-icon warning">📊</div>
                <div class="stat-card-value">${(summary.overall_attendance_avg || 0).toFixed(1)}%</div>
                <div class="stat-card-label">Average Attendance</div>
            </div>
            <div class="stat-card animate-fade-in-up stagger-3">
                <div class="stat-card-icon danger">⚠️</div>
                <div class="stat-card-value">${summary.total_defaulters || 0}</div>
                <div class="stat-card-label">Defaulters</div>
            </div>
        `;

        document.getElementById('stats-container').innerHTML = html;

        // Animate numbers
        animateNumbers();
    } catch (error) {
        showError('stats-container', 'Failed to load dashboard summary. Please refresh the page.');
    }
}

async function renderDefaultersTable() {
    showLoading('defaulters-container');

    try {
        const defaulters = await fetchDefaulters(20);

        if (!defaulters || defaulters.length === 0) {
            document.getElementById('defaulters-container').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                        </svg>
                    </div>
                    <h3 class="empty-state-title" style="color: var(--success);">All Clear!</h3>
                    <p class="empty-state-text">No defaulters! All students have good attendance.</p>
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

        defaulters.forEach((student, index) => {
            html += `
                <tr class="animate-fade-in" style="animation-delay: ${index * 0.1}s;">
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
// Number Animation
// ============================================

function animateNumbers() {
    const statValues = document.querySelectorAll('.stat-card-value');

    statValues.forEach(el => {
        const text = el.textContent;
        const num = parseFloat(text.replace(/[^0-9.]/g, ''));

        if (!isNaN(num) && num > 0) {
            const hasPercent = text.includes('%');
            const hasPlus = text.includes('+');

            let currentValue = 0;
            const increment = num / 50;
            const duration = 1500;
            const stepTime = duration / 50;

            const timer = setInterval(() => {
                currentValue += increment;
                if (currentValue >= num) {
                    currentValue = num;
                    clearInterval(timer);
                }

                let displayValue = currentValue < 100 ? Math.floor(currentValue) : currentValue.toFixed(1);
                if (hasPercent) displayValue += '%';
                if (hasPlus) displayValue += '+';

                el.textContent = displayValue;
            }, stepTime);
        }
    });
}

// ============================================
// Render Functions - Student Dashboard
// ============================================

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

async function renderStudentDetails(studentId) {
    if (!studentId) {
        document.getElementById('student-attendance-content').innerHTML = `
            <div class="empty-state glass-card animate-fade-in">
                <div class="empty-state-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                    </svg>
                </div>
                <h3 class="empty-state-title">No Student Selected</h3>
                <p class="empty-state-text">Please select a student from the dropdown above to view their attendance details.</p>
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

        const overallPct = attendanceData.overall_attendance || 0;
        const riskScore = riskData.risk_score || 0;

        const alertClass = riskData.is_impossible ? 'alert-danger' : riskData.is_at_risk ? 'alert-warning' : 'alert-success';
        const alertIcon = riskData.is_impossible ? '🚨' : riskData.is_at_risk ? '⚠️' : '✅';
        const alertStatus = riskData.is_impossible ? 'CRITICAL' : riskData.is_at_risk ? 'WARNING' : 'GOOD';

        let html = `
            <!-- Risk Alert -->
            <div class="alert ${alertClass} mb-4 animate-fade-in-up">
                <span style="font-size: 1.25rem;">${alertIcon}</span>
                <div>
                    <strong>${alertStatus}</strong>: ${riskData.recommendation || 'Student is on track.'}
                </div>
            </div>

            <!-- Stats Row -->
            <div class="stats-grid mb-4">
                <div class="stat-card animate-fade-in-up">
                    <div class="stat-card-icon primary">📊</div>
                    <div class="stat-card-value">${overallPct.toFixed(1)}%</div>
                    <div class="stat-card-label">Overall Attendance</div>
                </div>
                <div class="stat-card animate-fade-in-up stagger-1">
                    <div class="stat-card-icon ${riskData.is_at_risk ? 'danger' : 'success'}">⚠️</div>
                    <div class="stat-card-value">${riskScore.toFixed(0)}</div>
                    <div class="stat-card-label">Risk Score</div>
                </div>
                <div class="stat-card animate-fade-in-up stagger-2">
                    <div class="stat-card-icon warning">📅</div>
                    <div class="stat-card-value">${riskData.classes_remaining || 0}</div>
                    <div class="stat-card-label">Classes Remaining</div>
                </div>
                <div class="stat-card animate-fade-in-up stagger-3">
                    <div class="stat-card-icon success">✓</div>
                    <div class="stat-card-value">${riskData.min_classes_needed || 0}</div>
                    <div class="stat-card-label">Classes Needed</div>
                </div>
            </div>

            <!-- Risk Status -->
            <div class="card glass-card mb-4 animate-fade-in-up">
                <div class="card-header">
                    <h3 class="card-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        </svg>
                        Risk Assessment
                    </h3>
                </div>
                <div class="d-flex align-items-center gap-3">
                    ${getRiskBadge(riskScore, riskData.is_impossible)}
                    <span class="text-muted">Current: ${riskData.current_attendance_pct?.toFixed(1) || 0}% | Target: 75%</span>
                </div>
            </div>

            <!-- Subject-wise Table -->
            <div class="card glass-card mb-4 animate-fade-in-up">
                <div class="card-header">
                    <h3 class="card-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                            <polyline points="14 2 14 8 20 8"/>
                        </svg>
                        Subject-wise Attendance
                    </h3>
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
            attendanceData.subject_wise.forEach((subject, index) => {
                html += `
                    <tr class="animate-fade-in" style="animation-delay: ${index * 0.05}s;">
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
            <div class="card glass-card animate-fade-in-up">
                <div class="card-header">
                    <h3 class="card-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
                        </svg>
                        Monthly Attendance Trend
                    </h3>
                </div>
                <div class="chart-container">
                    <canvas id="monthlyTrendChart"></canvas>
                </div>
            </div>
        `;

        document.getElementById('student-attendance-content').innerHTML = html;

        // Render monthly trend chart with neon styling
        if (attendanceData.monthly_trend && attendanceData.monthly_trend.length > 0) {
            renderMonthlyTrendChart(attendanceData.monthly_trend);
        }

    } catch (error) {
        showError('student-attendance-content', 'Failed to load student attendance details.');
        console.error(error);
    }
}

// ============================================
// Chart Rendering - Neon Style
// ============================================

let monthlyTrendChartInstance = null;

function renderMonthlyTrendChart(monthlyData) {
    const ctx = document.getElementById('monthlyTrendChart');
    if (!ctx) return;

    if (monthlyTrendChartInstance) {
        monthlyTrendChartInstance.destroy();
    }

    const labels = monthlyData.map(d => d.month);
    const data = monthlyData.map(d => d.attendance_percentage);

    // Create gradient for chart
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(168, 85, 247, 0.5)');
    gradient.addColorStop(1, 'rgba(168, 85, 247, 0)');

    monthlyTrendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Attendance %',
                data: data,
                borderColor: '#a855f7',
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointHoverRadius: 9,
                pointBackgroundColor: '#06b6d4',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointShadow: {
                    color: 'rgba(168, 85, 247, 0.5)',
                    blur: 10
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(20, 20, 25, 0.95)',
                    titleColor: '#f9fafb',
                    bodyColor: '#d1d5db',
                    borderColor: 'rgba(168, 85, 247, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9ca3af',
                        callback: value => value + '%'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// ============================================
// Render Functions - Class Analytics
// ============================================

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
            subjectsAnalytics.forEach((subject, index) => {
                const avgAtt = subject.average_attendance || 0;
                const atRisk = subject.students_at_risk || 0;
                const totalStudents = subject.total_students || 0;

                html += `
                    <div class="card glass-card animate-fade-in-up" style="animation-delay: ${index * 0.1}s;">
                        <div class="card-header">
                            <h4 class="card-title mb-0">${subject.subject_code}</h4>
                            <span class="badge ${avgAtt >= 75 ? 'badge-success' : 'badge-danger'}">
                                ${avgAtt.toFixed(1)}%
                            </span>
                        </div>
                        <p class="text-muted mb-2" style="font-size: 0.85rem;">${subject.subject_name}</p>
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
            html += `<div class="empty-state glass-card"><p class="text-muted">No subject analytics data available.</p></div>`;
        }

        html += `
            </div>

            <!-- Average Attendance Chart -->
            <div class="card glass-card mb-4 animate-fade-in-up">
                <div class="card-header">
                    <h3 class="card-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
                        </svg>
                        Average Attendance by Subject
                    </h3>
                </div>
                <div class="chart-container large">
                    <canvas id="subjectAttendanceChart"></canvas>
                </div>
            </div>

            <!-- Top Defaulters -->
            <div class="card glass-card animate-fade-in-up">
                <div class="card-header">
                    <h3 class="card-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                        </svg>
                        Students Requiring Attention
                    </h3>
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

            defaulters.forEach((student, index) => {
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
                    <tr class="animate-fade-in" style="animation-delay: ${index * 0.08}s;">
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
                <div class="empty-state">
                    <div class="empty-state-icon" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                        </svg>
                    </div>
                    <h3 class="empty-state-title" style="color: var(--success);">All Clear!</h3>
                    <p class="empty-state-text">No defaulters! All students have good attendance.</p>
                </div>
            `;
        }

        html += `</div>`;

        document.getElementById('class-analytics-content').innerHTML = html;

        // Render subject attendance chart with neon styling
        if (subjectsAnalytics && subjectsAnalytics.length > 0) {
            renderSubjectAttendanceChart(subjectsAnalytics);
        }

    } catch (error) {
        showError('class-analytics-content', 'Failed to load class analytics.');
        console.error(error);
    }
}

// ============================================
// Chart Rendering - Subject Bar Chart (Neon)
// ============================================

let subjectAttendanceChartInstance = null;

function renderSubjectAttendanceChart(subjectsData) {
    const ctx = document.getElementById('subjectAttendanceChart');
    if (!ctx) return;

    if (subjectAttendanceChartInstance) {
        subjectAttendanceChartInstance.destroy();
    }

    const labels = subjectsData.map(s => s.subject_code);
    const data = subjectsData.map(s => s.average_attendance);
    const backgroundColors = data.map(att => {
        if (att >= 75) return 'rgba(16, 185, 129, 0.8)';
        if (att >= 60) return 'rgba(245, 158, 11, 0.8)';
        return 'rgba(239, 68, 68, 0.8)';
    });

    const borderColors = data.map(att => {
        if (att >= 75) return '#10b981';
        if (att >= 60) return '#f59e0b';
        return '#ef4444';
    });

    subjectAttendanceChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Attendance %',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 12,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(20, 20, 25, 0.95)',
                    titleColor: '#f9fafb',
                    bodyColor: '#d1d5db',
                    borderColor: 'rgba(168, 85, 247, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9ca3af',
                        callback: value => value + '%'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// ============================================
// FAB Menu Handler
// ============================================

function initFabMenu() {
    const fab = document.getElementById('student-fab');
    const fabMenu = document.getElementById('student-fab-menu');

    if (!fab || !fabMenu) return;

    fab.addEventListener('click', (e) => {
        e.stopPropagation();
        fabMenu.classList.toggle('open');
    });

    fabMenu.addEventListener('click', (event) => {
        const target = event.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;
        if (!action) return;

        // Handle FAB actions
        const actionLabels = {
            create: 'Create Student',
            update: 'Update Student',
            delete: 'Delete Student'
        };

        console.log(`FAB Action: ${action}`);
        alert(`${actionLabels[action]} - This feature can be connected to APIs.`);
        fabMenu.classList.remove('open');
    });

    // Close on outside click
    document.addEventListener('click', (event) => {
        if (!fabMenu.contains(event.target) && event.target !== fab) {
            fabMenu.classList.remove('open');
        }
    });
}

// ============================================
// Navbar Scroll Effect
// ============================================

function initNavbarScroll() {
    const navbar = document.getElementById('main-navbar');
    if (!navbar) return;

    const handleScroll = () => {
        if (window.scrollY > 24) {
            navbar.classList.add('navbar-solid');
        } else {
            navbar.classList.remove('navbar-solid');
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
}

// ============================================
// GSAP Animations
// ============================================

function initGsapAnimations() {
    if (!window.gsap) return;

    // Hero animations
    const hero = document.querySelector('.hero-section');
    if (hero) {
        const tl = gsap.timeline();

        tl.from('.hero-badge', {
            opacity: 0,
            y: 20,
            duration: 0.6,
            ease: 'power2.out'
        })
        .from('.hero-title', {
            opacity: 0,
            y: 30,
            duration: 0.7,
            ease: 'power3.out'
        }, '-=0.4')
        .from('.hero-subtitle', {
            opacity: 0,
            y: 20,
            duration: 0.6
        }, '-=0.3')
        .from('.hero-cta .btn', {
            opacity: 0,
            y: 15,
            duration: 0.5,
            stagger: 0.1
        }, '-=0.3')
        .from('.hero-metric-card', {
            opacity: 0,
            y: 20,
            duration: 0.5,
            stagger: 0.1
        }, '-=0.2');
    }

    // Feature cards animation
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards.length > 0) {
        gsap.from(featureCards, {
            scrollTrigger: {
                trigger: '.features-section',
                start: 'top 80%'
            },
            opacity: 0,
            y: 40,
            duration: 0.6,
            stagger: 0.1,
            ease: 'power2.out'
        });
    }
}

// ============================================
// Page Initialization
// ============================================

function initLandingPage() {
    renderDashboardSummary();
    renderDefaultersTable();
}

function initStudentDashboard() {
    populateStudentDropdown();

    const studentSelect = document.getElementById('student-select');
    if (studentSelect) {
        studentSelect.addEventListener('change', (e) => {
            renderStudentDetails(e.target.value);
        });
    }

    initFabMenu();
}

function initClassAnalytics() {
    renderClassAnalytics();
}

// ============================================
// DOM Ready
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize cursor glow
    initCursorGlow();

    // Initialize particles
    initParticles();

    // Initialize navbar scroll
    initNavbarScroll();

    // Initialize GSAP animations
    setTimeout(() => {
        initGsapAnimations();
    }, 100);

    // Get current page
    const pageId = document.body.getAttribute('data-page');

    // Initialize page-specific logic
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
