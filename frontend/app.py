"""
Streamlit Dashboard for College Attendance Analytics.
Production-ready frontend with interactive visualizations.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, date

# ============== Page Configuration ==============

st.set_page_config(
    page_title="Attendance Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== Configuration ==============

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .risk-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .risk-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .risk-low {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============== Helper Functions ==============

@st.cache_data(ttl=60)
def fetch_data(endpoint: str, params: dict = None) -> dict:
    """Fetch data from API with caching."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return {}


@st.cache_data(ttl=300)
def fetch_all_students() -> list:
    """Fetch all students."""
    data = fetch_data("/students/", {"limit": 500})
    return data.get("items", []) if isinstance(data, dict) else []


@st.cache_data(ttl=300)
def fetch_all_subjects() -> list:
    """Fetch all subjects."""
    data = fetch_data("/subjects/", {"limit": 100})
    return data.get("items", []) if isinstance(data, dict) else []


def get_attendance_status(percentage: float) -> tuple:
    """Get status color and icon for attendance percentage."""
    if percentage >= 90:
        return "🟢 Excellent", "#4caf50"
    elif percentage >= 75:
        return "🟢 Good", "#8bc34a"
    elif percentage >= 60:
        return "🟡 Average", "#ffc107"
    elif percentage >= 50:
        return "🟠 Poor", "#ff9800"
    else:
        return "🔴 Critical", "#f44336"


def create_gauge_chart(value: float, title: str, max_value: float = 100) -> go.Figure:
    """Create a gauge chart for attendance percentage."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        delta={'reference': 75, 'increasing': {'color': "#4caf50"}, 'decreasing': {'color': "#f44336"}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': get_gauge_color(value)},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': "#ffebee"},
                {'range': [50, 60], 'color': "#fff3e0"},
                {'range': [60, 75], 'color': "#fffde7"},
                {'range': [75, 90], 'color': "#f1f8e9"},
                {'range': [90, 100], 'color': "#e8f5e9"}
            ],
            'threshold': {
                'line': {'color': "#f44336", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    fig.update_layout(height=250, margin={'l': 20, 'r': 20, 't': 40, 'b': 20})
    return fig


def get_gauge_color(value: float) -> str:
    """Get gauge bar color based on value."""
    if value >= 90:
        return "#2e7d32"
    elif value >= 75:
        return "#66bb6a"
    elif value >= 60:
        return "#ffa726"
    elif value >= 50:
        return "#ef6c00"
    else:
        return "#d32f2f"


# ============== Sidebar ==============

st.sidebar.title("🎓 Attendance Dashboard")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "👤 Student Analytics", "📚 Subject Analytics", "⚠️ Risk Assessment", "🤖 ML Prediction"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

# Fetch dashboard summary
dashboard_summary = fetch_data("/analytics/dashboard/summary")

if dashboard_summary:
    st.sidebar.metric("Total Students", dashboard_summary.get("total_students", 0))
    st.sidebar.metric("Total Subjects", dashboard_summary.get("total_subjects", 0))
    st.sidebar.metric("Avg Attendance", f"{dashboard_summary.get('overall_attendance_avg', 0):.1f}%")
    st.sidebar.metric("Defaulters", dashboard_summary.get("total_defaulters", 0))

st.sidebar.markdown("---")
st.sidebar.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

# ============== Dashboard Page ==============

if page == "📊 Dashboard":
    st.title("📊 Attendance Analytics Dashboard")
    st.markdown("### Overview")
    
    if dashboard_summary:
        # Top metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Students",
                value=dashboard_summary.get("total_students", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Subjects",
                value=dashboard_summary.get("total_subjects", 0),
                delta=None
            )
        
        with col3:
            avg_attendance = dashboard_summary.get("overall_attendance_avg", 0)
            st.metric(
                label="Overall Attendance",
                value=f"{avg_attendance:.1f}%",
                delta="Above 75%" if avg_attendance >= 75 else "Below 75%"
            )
        
        with col4:
            defaulters = dashboard_summary.get("total_defaulters", 0)
            high_risk = dashboard_summary.get("students_at_high_risk", 0)
            st.metric(
                label="Defaulters",
                value=defaulters,
                delta=f"{high_risk} high risk" if high_risk > 0 else None
            )
        
        st.markdown("---")
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Attendance Distribution")
            
            # Fetch defaulters data for visualization
            defaulters_data = fetch_data("/analytics/dashboard/defaulters", {"limit": 50})
            
            if defaulters_data:
                df_defaulters = pd.DataFrame(defaulters_data)
                if not df_defaulters.empty:
                    fig = px.histogram(
                        df_defaulters,
                        x="attendance_percentage",
                        nbins=20,
                        title="Attendance Distribution of Defaulters",
                        labels={"attendance_percentage": "Attendance %"},
                        color_discrete_sequence=["#f44336"]
                    )
                    fig.update_layout(showlegend=False, height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No defaulters found!")
            else:
                st.info("No data available")
        
        with col2:
            st.subheader("🎯 Target vs Actual")
            
            target_data = {
                "Metric": ["Target", "Actual Average"],
                "Attendance %": [75, dashboard_summary.get("overall_attendance_avg", 0)]
            }
            df_target = pd.DataFrame(target_data)
            
            fig = px.bar(
                df_target,
                x="Metric",
                y="Attendance %",
                title="Target vs Actual Attendance",
                color="Attendance %",
                color_continuous_scale=["#f44336", "#4caf50"]
            )
            fig.update_layout(showlegend=False, height=350)
            fig.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="75% Target")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent defaulters table
        st.markdown("---")
        st.subheader("⚠️ Students Requiring Attention")
        
        if defaulters_data:
            df_defaulters = pd.DataFrame(defaulters_data)
            if not df_defaulters.empty:
                # Add status column
                df_defaulters["status"] = df_defaulters["attendance_percentage"].apply(
                    lambda x: get_attendance_status(x)[0]
                )
                
                # Display top 10 defaulters
                st.dataframe(
                    df_defaulters.head(10)[["roll_number", "name", "department", "attendance_percentage", "status"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("🎉 No defaulters! All students have good attendance.")
        else:
            st.info("No data available")

# ============== Student Analytics Page ==============

elif page == "👤 Student Analytics":
    st.title("👤 Student Analytics")
    
    # Fetch students
    students = fetch_all_students()
    
    if students:
        # Student selector
        student_options = {f"{s['roll_number']} - {s['name']}": s for s in students}
        selected = st.selectbox(
            "Select Student",
            options=list(student_options.keys())
        )
        
        if selected:
            student = student_options[selected]
            student_id = student["id"]
            
            # Student info cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"**Roll No:** {student['roll_number']}")
            with col2:
                st.info(f"**Name:** {student['name']}")
            with col3:
                st.info(f"**Department:** {student['department']}")
            with col4:
                st.info(f"**Semester:** {student['semester']}")
            
            st.markdown("---")
            
            # Fetch student analytics
            trend_data = fetch_data(f"/attendance/analytics/student/{student_id}/complete")
            
            if trend_data:
                # Overall attendance gauge
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    overall_pct = trend_data.get("overall_attendance", 0)
                    status, color = get_attendance_status(overall_pct)
                    st.metric("Overall Attendance", f"{overall_pct:.1f}%", delta=status)
                    
                    fig_gauge = create_gauge_chart(overall_pct, "Attendance Gauge")
                    st.plotly_chart(fig_gauge, use_container_width=True)
                
                with col2:
                    # Subject-wise bar chart
                    subject_wise = trend_data.get("subject_wise", [])
                    if subject_wise:
                        df_subject = pd.DataFrame(subject_wise)
                        
                        fig = px.bar(
                            df_subject,
                            x="subject_code",
                            y="attendance_percentage",
                            color="attendance_percentage",
                            color_continuous_scale="RdYlGn",
                            title="Subject-wise Attendance",
                            labels={"subject_code": "Subject", "attendance_percentage": "Attendance %"}
                        )
                        fig.update_layout(height=300)
                        fig.add_hline(y=75, line_dash="dash", line_color="red")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Monthly trend line chart
                st.markdown("---")
                st.subheader("📈 Monthly Attendance Trend")
                
                monthly_trend = trend_data.get("monthly_trend", [])
                if monthly_trend:
                    df_monthly = pd.DataFrame(monthly_trend)
                    
                    fig = px.line(
                        df_monthly,
                        x="month",
                        y="attendance_percentage",
                        markers=True,
                        title="Monthly Attendance Trend",
                        labels={"month": "Month", "attendance_percentage": "Attendance %"}
                    )
                    fig.update_traces(line=dict(width=3, color="#2196f3"))
                    fig.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="75% Target")
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Risk assessment
                st.markdown("---")
                st.subheader("⚠️ Risk Assessment")
                
                risk_data = fetch_data(f"/analytics/risk/student/{student_id}")
                
                if risk_data:
                    risk_score = risk_data.get("risk_score", 0)
                    is_at_risk = risk_data.get("is_at_risk", False)
                    is_impossible = risk_data.get("is_impossible", False)
                    
                    if is_impossible:
                        st.error(f"🚨 **CRITICAL**: {risk_data.get('recommendation', '')}")
                    elif is_at_risk:
                        st.warning(f"⚠️ **WARNING**: {risk_data.get('recommendation', '')}")
                    else:
                        st.success(f"✅ {risk_data.get('recommendation', '')}")
                    
                    # Risk metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Risk Score",
                            f"{risk_score:.1f}/100",
                            delta="High Risk" if risk_score >= 70 else "Medium Risk" if risk_score >= 40 else "Low Risk"
                        )
                    with col2:
                        st.metric(
                            "Classes Remaining",
                            risk_data.get("classes_remaining", 0)
                        )
                    with col3:
                        st.metric(
                            "Min Classes Needed",
                            risk_data.get("min_classes_needed", 0)
                        )
            else:
                st.info("No attendance data available for this student.")
    else:
        st.info("No students found. Please add students first.")

# ============== Subject Analytics Page ==============

elif page == "📚 Subject Analytics":
    st.title("📚 Subject Analytics")
    
    subjects = fetch_all_subjects()
    
    if subjects:
        subject_options = {f"{s['subject_code']} - {s['subject_name']}": s for s in subjects}
        selected = st.selectbox(
            "Select Subject",
            options=list(subject_options.keys())
        )
        
        if selected:
            subject = subject_options[selected]
            subject_id = subject["id"]
            
            # Subject info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Code:** {subject['subject_code']}")
            with col2:
                st.info(f"**Credits:** {subject['credits']}")
            with col3:
                st.info(f"**Total Classes:** {subject['total_classes_required']}")
            
            st.markdown("---")
            
            # Fetch class analytics
            class_analytics = fetch_data(f"/analytics/class/subject/{subject_id}")
            
            if class_analytics:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Students", class_analytics.get("total_students", 0))
                
                with col2:
                    avg_att = class_analytics.get("average_attendance", 0)
                    st.metric("Average Attendance", f"{avg_att:.1f}%")
                
                with col3:
                    at_risk = class_analytics.get("students_at_risk", 0)
                    st.metric("At Risk", at_risk, delta_color="inverse")
                
                with col4:
                    defaulter_pct = class_analytics.get("defaulter_percentage", 0)
                    st.metric("Defaulter %", f"{defaulter_pct:.1f}%")
                
                # Pie chart for risk distribution
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    safe = class_analytics.get("students_safe", 0)
                    at_risk = class_analytics.get("students_at_risk", 0)
                    
                    df_pie = pd.DataFrame({
                        "Category": ["Safe (≥75%)", "At Risk (<75%)"],
                        "Students": [safe, at_risk]
                    })
                    
                    fig = px.pie(
                        df_pie,
                        values="Students",
                        names="Category",
                        title="Student Distribution",
                        color="Category",
                        color_discrete_map={"Safe (≥75%)": "#4caf50", "At Risk (<75%)": "#f44336"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### Subject Performance Summary")
                    
                    if class_analytics.get("average_attendance", 0) >= 75:
                        st.success(f"✅ Class average is above 75% target")
                    else:
                        st.error(f"⚠️ Class average is below 75% target")
                    
                    if class_analytics.get("students_at_risk", 0) > class_analytics.get("students_safe", 0):
                        st.warning("⚠️ Majority of students are at risk!")
                    else:
                        st.success("✅ Majority of students are on track")
            else:
                st.info("No analytics data available for this subject.")
    else:
        st.info("No subjects found. Please add subjects first.")

# ============== Risk Assessment Page ==============

elif page == "⚠️ Risk Assessment":
    st.title("⚠️ Risk Assessment")
    st.markdown("Identify students at risk of falling below 75% attendance")
    
    # Fetch all at-risk students
    at_risk_data = fetch_data("/analytics/risk/all-at-risk")
    
    if at_risk_data:
        df_risk = pd.DataFrame(at_risk_data)
        
        if not df_risk.empty:
            # Summary cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_risk = len(df_risk[df_risk["risk_score"] >= 70])
                st.metric("High Risk Students", high_risk)
            
            with col2:
                medium_risk = len(df_risk[(df_risk["risk_score"] >= 40) & (df_risk["risk_score"] < 70)])
                st.metric("Medium Risk Students", medium_risk)
            
            with col3:
                impossible = len(df_risk[df_risk["is_impossible"] == True])
                st.metric("Critical (Impossible)", impossible)
            
            st.markdown("---")
            
            # Filter by risk level
            risk_filter = st.selectbox(
                "Filter by Risk Level",
                ["All", "High Risk (≥70)", "Medium Risk (40-69)", "Low Risk (<40)", "Critical (Impossible)"]
            )
            
            filtered_df = df_risk.copy()
            
            if risk_filter == "High Risk (≥70)":
                filtered_df = df_risk[df_risk["risk_score"] >= 70]
            elif risk_filter == "Medium Risk (40-69)":
                filtered_df = df_risk[(df_risk["risk_score"] >= 40) & (df_risk["risk_score"] < 70)]
            elif risk_filter == "Low Risk (<40)":
                filtered_df = df_risk[df_risk["risk_score"] < 40]
            elif risk_filter == "Critical (Impossible)":
                filtered_df = df_risk[df_risk["is_impossible"] == True]
            
            # Display table
            display_cols = ["student_name", "current_attendance_pct", "risk_score", 
                          "classes_remaining", "min_classes_needed", "is_impossible"]
            
            for _, row in filtered_df.iterrows():
                if row["is_impossible"]:
                    st.error(f"🚨 **{row['student_name']}** - Risk Score: {row['risk_score']:.1f} | "
                            f"Current: {row['current_attendance_pct']:.1f}% | "
                            f"Status: Mathematically Impossible to reach 75%")
                elif row["risk_score"] >= 70:
                    st.error(f"⚠️ **{row['student_name']}** - Risk Score: {row['risk_score']:.1f} | "
                            f"Current: {row['current_attendance_pct']:.1f}% | "
                            f"Needs: {row['min_classes_needed']}/{row['classes_remaining']} classes")
                elif row["risk_score"] >= 40:
                    st.warning(f"⚡ **{row['student_name']}** - Risk Score: {row['risk_score']:.1f} | "
                              f"Current: {row['current_attendance_pct']:.1f}%")
                else:
                    st.info(f"📊 **{row['student_name']}** - Risk Score: {row['risk_score']:.1f}")
            
            st.markdown("---")
            st.subheader("Detailed Risk Table")
            st.dataframe(
                filtered_df[display_cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("🎉 No students at risk! All students have good attendance.")
    else:
        st.info("No risk data available.")

# ============== ML Prediction Page ==============

elif page == "🤖 ML Prediction":
    st.title("🤖 ML-Based Risk Prediction")
    st.markdown("""
    Predict the probability of a student falling below 75% attendance using Logistic Regression.
    
    **Feature Importance:**
    - Current Attendance % (45%): Most predictive feature
    - Classes Remaining (25%): Opportunity to improve
    - Classes Attended (15%): Engagement indicator
    - Historical Trend (10%): Direction of change
    - Subject Difficulty (5%): External factor
    """)
    
    st.markdown("---")
    
    # Input form
    col1, col2 = st.columns(2)
    
    with col1:
        current_attendance = st.slider(
            "Current Attendance %",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=0.5
        )
        
        classes_attended = st.slider(
            "Classes Attended So Far",
            min_value=0,
            max_value=100,
            value=40
        )
    
    with col2:
        classes_remaining = st.slider(
            "Classes Remaining",
            min_value=0,
            max_value=60,
            value=20
        )
        
        subject_difficulty = st.slider(
            "Subject Difficulty (0-1)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1
        )
    
    historical_trend = st.slider(
        "Historical Attendance Trend (-1 = Declining, 0 = Stable, +1 = Improving)",
        min_value=-1.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )
    
    if st.button("🔮 Predict Risk", type="primary"):
        # Prepare prediction request
        prediction_input = {
            "current_attendance_pct": current_attendance,
            "classes_attended": classes_attended,
            "classes_remaining": classes_remaining,
            "subject_difficulty": subject_difficulty,
            "historical_attendance_trend": historical_trend
        }
        
        # Call prediction API
        try:
            response = requests.post(
                f"{API_BASE_URL}/analytics/risk/predict",
                json=prediction_input,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                probability = result.get("probability_of_shortage", 0)
                risk_category = result.get("risk_category", "Unknown")
                confidence = result.get("confidence", 0)
                feature_importance = result.get("feature_importance", {})
                
                # Display results
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if risk_category == "High":
                        st.error(f"**Risk Category:** {risk_category}")
                    elif risk_category == "Medium":
                        st.warning(f"**Risk Category:** {risk_category}")
                    else:
                        st.success(f"**Risk Category:** {risk_category}")
                
                with col2:
                    st.metric("Shortage Probability", f"{probability:.1%}")
                
                with col3:
                    st.metric("Model Confidence", f"{confidence:.1%}")
                
                # Progress bar for probability
                st.markdown("### Probability of Falling Below 75%")
                st.progress(probability)
                
                # Feature importance chart
                if feature_importance:
                    st.markdown("---")
                    st.markdown("### Feature Importance")
                    
                    df_importance = pd.DataFrame({
                        "Feature": list(feature_importance.keys()),
                        "Importance": list(feature_importance.values())
                    })
                    
                    fig = px.bar(
                        df_importance,
                        x="Importance",
                        y="Feature",
                        orientation="h",
                        color="Importance",
                        color_continuous_scale="Blues"
                    )
                    fig.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Recommendation
                st.markdown("---")
                st.markdown("### Recommendation")
                
                if probability >= 0.7:
                    st.error("""
                    **🚨 HIGH RISK**: Student has a high probability of falling below 75%.
                    
                    **Action Required:**
                    - Immediate intervention needed
                    - Counsel student on attendance importance
                    - Consider medical/personal issues
                    - Set up attendance monitoring plan
                    """)
                elif probability >= 0.4:
                    st.warning("""
                    **⚠️ MEDIUM RISK**: Student may fall below 75% without improvement.
                    
                    **Recommended Actions:**
                    - Monitor attendance closely
                    - Send attendance warnings
                    - Encourage class participation
                    """)
                else:
                    st.success("""
                    **✅ LOW RISK**: Student is likely to maintain safe attendance.
                    
                    **Continue:**
                    - Regular monitoring
                    - Positive reinforcement
                    """)
            else:
                st.error(f"Prediction failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to prediction service: {str(e)}")
            st.info("Note: ML prediction requires the backend API to be running.")

# ============== Footer ==============

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        College Attendance Analytics Dashboard | Built with FastAPI + Streamlit + Plotly
    </div>
    """,
    unsafe_allow_html=True
)
