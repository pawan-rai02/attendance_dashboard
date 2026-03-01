"""
Reusable Streamlit components for the attendance dashboard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, Any


def create_metric_card(
    label: str,
    value: Any,
    delta: Optional[str] = None,
    delta_color: str = "normal"
):
    """Create a styled metric card."""
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color
    )


def create_attendance_gauge(
    value: float,
    title: str = "Attendance",
    max_value: float = 100
) -> go.Figure:
    """
    Create a gauge chart for attendance percentage.
    
    Args:
        value: Current attendance percentage
        title: Chart title
        max_value: Maximum value for gauge
        
    Returns:
        Plotly Figure object
    """
    # Determine color based on value
    if value >= 90:
        color = "#2e7d32"
    elif value >= 75:
        color = "#66bb6a"
    elif value >= 60:
        color = "#ffa726"
    elif value >= 50:
        color = "#ef6c00"
    else:
        color = "#d32f2f"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        delta={'reference': 75},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'steps': [
                {'range': [0, 50], 'color': "#ffebee"},
                {'range': [50, 75], 'color': "#fff3e0"},
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


def create_monthly_trend_chart(
    monthly_data: list,
    title: str = "Monthly Attendance Trend"
) -> go.Figure:
    """
    Create a line chart for monthly attendance trend.
    
    Args:
        monthly_data: List of dicts with 'month' and 'attendance_percentage'
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame(monthly_data)
    
    fig = px.line(
        df,
        x="month",
        y="attendance_percentage",
        markers=True,
        title=title,
        labels={"month": "Month", "attendance_percentage": "Attendance %"}
    )
    
    fig.update_traces(line=dict(width=3, color="#2196f3"))
    fig.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="75% Target")
    fig.update_layout(height=350)
    
    return fig


def create_subject_wise_bar_chart(
    subject_data: list,
    title: str = "Subject-wise Attendance"
) -> go.Figure:
    """
    Create a bar chart for subject-wise attendance.
    
    Args:
        subject_data: List of dicts with 'subject_code' and 'attendance_percentage'
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame(subject_data)
    
    fig = px.bar(
        df,
        x="subject_code",
        y="attendance_percentage",
        color="attendance_percentage",
        color_continuous_scale="RdYlGn",
        title=title,
        labels={"subject_code": "Subject", "attendance_percentage": "Attendance %"}
    )
    
    fig.update_layout(height=300)
    fig.add_hline(y=75, line_dash="dash", line_color="red")
    
    return fig


def create_risk_distribution_pie(
    safe_count: int,
    at_risk_count: int,
    title: str = "Risk Distribution"
) -> go.Figure:
    """
    Create a pie chart for risk distribution.
    
    Args:
        safe_count: Number of students with >= 75% attendance
        at_risk_count: Number of students with < 75% attendance
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame({
        "Category": ["Safe (≥75%)", "At Risk (<75%)"],
        "Students": [safe_count, at_risk_count]
    })
    
    fig = px.pie(
        df,
        values="Students",
        names="Category",
        title=title,
        color="Category",
        color_discrete_map={"Safe (≥75%)": "#4caf50", "At Risk (<75%)": "#f44336"}
    )
    
    fig.update_layout(height=350)
    
    return fig


def create_risk_alert_box(
    student_name: str,
    risk_score: float,
    current_attendance: float,
    is_impossible: bool = False,
    recommendation: str = ""
):
    """
    Display a risk alert box for a student.
    
    Args:
        student_name: Name of the student
        risk_score: Risk score (0-100)
        current_attendance: Current attendance percentage
        is_impossible: Whether it's mathematically impossible to reach 75%
        recommendation: Actionable recommendation
    """
    if is_impossible:
        st.error(f"🚨 **{student_name}** - CRITICAL (Risk: {risk_score:.1f})\n\n{recommendation}")
    elif risk_score >= 70:
        st.error(f"⚠️ **{student_name}** - HIGH RISK (Risk: {risk_score:.1f}, Attendance: {current_attendance:.1f}%)\n\n{recommendation}")
    elif risk_score >= 40:
        st.warning(f"⚡ **{student_name}** - MEDIUM RISK (Risk: {risk_score:.1f}, Attendance: {current_attendance:.1f}%)\n\n{recommendation}")
    else:
        st.info(f"📊 **{student_name}** - LOW RISK (Risk: {risk_score:.1f}, Attendance: {current_attendance:.1f}%)")


def create_dashboard_summary_cards(summary_data: Dict[str, Any]):
    """
    Display dashboard summary metric cards.
    
    Args:
        summary_data: Dictionary with dashboard metrics
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", summary_data.get("total_students", 0))
    
    with col2:
        st.metric("Total Subjects", summary_data.get("total_subjects", 0))
    
    with col3:
        avg = summary_data.get("overall_attendance_avg", 0)
        st.metric("Avg Attendance", f"{avg:.1f}%", 
                 delta="Above Target" if avg >= 75 else "Below Target")
    
    with col4:
        defaulters = summary_data.get("total_defaulters", 0)
        st.metric("Defaulters", defaulters, delta_color="inverse")
