import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & THEME STATE
# ==========================================
st.set_page_config(
    page_title="FocusForge: Adaptive Study Analytics", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States (In-memory storage)
if "subjects" not in st.session_state:
    st.session_state.subjects = ["Math", "Physics", "English", "History", "Chemistry"]

if "study_logs" not in st.session_state:
    # Initialize with 5 starter sessions so the charts aren't blank initially
    initial_data = [
        {"Date": "2026-07-10", "Hour": 14, "Subject": "Math", "Duration_Min": 45, "Distractions": 3, "Focus_Rating": 4},
        {"Date": "2026-07-11", "Hour": 16, "Subject": "Physics", "Duration_Min": 60, "Distractions": 5, "Focus_Rating": 3},
        {"Date": "2026-07-12", "Hour": 10, "Subject": "English", "Duration_Min": 30, "Distractions": 1, "Focus_Rating": 5},
        {"Date": "2026-07-13", "Hour": 19, "Subject": "History", "Duration_Min": 50, "Distractions": 2, "Focus_Rating": 4},
        {"Date": "2026-07-14", "Hour": 15, "Subject": "Chemistry", "Duration_Min": 40, "Distractions": 4, "Focus_Rating": 3}
    ]
    st.session_state.study_logs = pd.DataFrame(initial_data)

# ==========================================
# 2. ACCESSIBILITY SETTINGS (SIDEBAR)
# ==========================================
st.sidebar.title("♿ Accessibility Settings")
st.sidebar.write("Customize your layout workflow:")

# Toggles for Accessible Modes
adhd_mode = st.sidebar.toggle("🧠 Enable ADHD Focus Mode", value=False)
colorblind_mode = st.sidebar.toggle("👁️ Enable Colorblind Safe Mode", value=False)

# Theme Configuration
if colorblind_mode:
    # Okabe-Ito Universal Barrier-Free Palette
    COLOR_PALETTE = ["#0072B2", "#E69F00", "#009E73", "#F0E442", "#CC79A7", "#56B4E9", "#D55E00"]
    SEQUENTIAL_COLORS = px.colors.sequential.Viridis
else:
    # Standard high-vibrancy palette
    COLOR_PALETTE = ["#FF4B4B", "#1F77B4", "#2CA02C", "#9467BD", "#FF7F0E", "#17BECF", "#E377C2"]
    SEQUENTIAL_COLORS = px.colors.sequential.Oranges

# Dynamic Style Injections for ADHD Focus Mode
if adhd_mode:
    st.markdown("""
        <style>
        body, p, span, label, input, select {
            font-size: 1.15rem !important;
            letter-spacing: 0.06rem !important;
            line-height: 1.7 !important;
        }
        h1, h2, h3 {
            color: #0072B2 !important;
            font-weight: 800 !important;
        }
        .stButton>button {
            border: 2px solid #0072B2 !important;
            border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Helper function to generate Bionic Reading styles
def format_text(text):
    if adhd_mode:
        words = text.split()
        bionic_words = []
        for word in words:
            mid = max(1, len(word) // 2)
            bionic_words.append(f"**{word[:mid]}**{word[mid:]}")
        return " ".join(bionic_words)
    return text

# ==========================================
# 3. INTERACTIVE SUBJECT MANAGER & LOG INPUTS
# ==========================================
st.title("🎯 FocusForge")
st.markdown(format_text("An adaptive workspace analyzing cognitive performance data to help high schoolers learn how they work best."))
st.write("---")

# Layout columns for data entry and customization
col_setup, col_log = st.columns(2)

with col_setup:
    st.subheader("📚 1. Manage Your Subjects")
    st.write(format_text("Add your academic courses below to customize your metrics metrics telemetry."))
    
    # Simple form to add a custom subject
    with st.form("add_subject_form", clear_on_submit=True):
        new_subject = st.text_input("Add a New Course Name (e.g., Biology, Calculus):").strip()
        submit_subj = st.form_submit_button("Add Course to Database")
        if submit_subj and new_subject:
            if new_subject not in st.session_state.subjects:
                st.session_state.subjects.append(new_subject)
                st.success(f"Added {new_subject} to your program!")
            else:
                st.warning("That subject already exists.")
                
    # Show active subjects
    st.write("**Current Program Courses:** " + ", ".join(st.session_state.subjects))

with col_log:
    st.subheader("✏️ 2. Log a Study Session")
    st.write(format_text("When you finish a study sprint, record your focus variables to log the raw telemetry data."))
    
    with st.form("log_session_form", clear_on_submit=True):
        # Interactive Inputs utilizing the custom subjects list
        selected_subject = st.selectbox("Subject:", options=st.session_state.subjects)
        session_date = st.date_input("Date:", value=datetime.today())
        session_time = st.slider("Time of Day (Hour starting):", min_value=0, max_value=23, value=15)
        duration = st.number_input("Session Duration (Minutes):", min_value=5, max_value=240, value=30, step=5)
        distractions = st.number_input("Distraction Count (Clicks away/tab changes):", min_value=0, max_value=50, value=2)
        focus = st.slider("Rate Focus Level (1 = scattered, 5 = hyperfocus):", min_value=1, max_value=5, value=4)
        
        submit_log = st.form_submit_button("Submit Data Entry")
        if submit_log:
            new_log = {
                "Date": str(session_date),
                "Hour": int(session_time),
                "Subject": selected_subject,
                "Duration_Min": int(duration),
                "Distractions": int(distractions),
                "Focus_Rating": int(focus)
            }
            # Append to session logs dataframe
            st.session_state.study_logs = pd.concat([
                st.session_state.study_logs, 
                pd.DataFrame([new_log])
            ], ignore_index=True)
            st.success("Session data successfully saved to the active database!")

st.write("---")

# Safe Reference copy of the main database
df_active = st.session_state.study_logs.copy()

# ==========================================
# 4. ADAPTIVE METRICS & ANALYTICS RENDERING
# ==========================================

if adhd_mode:
    # --------------------------------------
    # ADHD LAYOUT (Low friction, highly-focused workflow)
    # --------------------------------------
    st.header("🧠 ADHD Minimalist Study Lounge")
    st.info("Reduced clutter mode active. Multi-column structures, high-frequency alerts, and competitive graphs are disabled.")
    
    col_adhd_1, col_adhd_2 = st.columns([1, 1])
    
    with col_adhd_1:
        st.write("### ⏱️ Quick Focus Sprint Timer")
        st.write(format_text("Use this to block external visual distractions. Run a quick study session right inside your workspace."))
        minutes = st.number_input("Sprint Duration (Minutes):", min_value=1, max_value=120, value=25)
        
        if st.button("Activate Visual Timer Block"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            for percent_complete in range(100):
                time.sleep(0.01)  # High-speed simulation for presentation convenience
                progress_bar.progress(percent_complete + 1)
                status_text.text(f"Focus Mode Locked... Progress: {percent_complete + 1}%")
            st.balloons()
            st.success("Excellent study block! Time to stretch.")

    with col_adhd_2:
        st.write("### 📊 Your Core Focus Windows")
        # Simple analysis: Average focus per subject using accessible color map
        subj_focus = df_active.groupby("Subject")["Focus_Rating"].mean().reset_index()
        fig_adhd = px.bar(
            subj_focus,
            x="Subject",
            y="Focus_Rating",
            color="Subject",
            title="Focus Accuracy Rating by Course (Simplifed View)",
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_adhd.update_layout(yaxis_range=[0, 5.5], margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_adhd, use_container_width=True)

else:
    # --------------------------------------
    # STANDARD ANALYTICS LAYOUT (Multi-dimensional visual metrics)
    # --------------------------------------
    st.header("📊 Deep Telemetry Metrics Dashboard")
    
    # 1. Row of High-Level Key Performance Indicators
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    total_hours = round(df_active["Duration_Min"].sum() / 60, 1)
    avg_distract = round(df_active["Distractions"].mean(), 1)
    avg_focus = round(df_active["Focus_Rating"].mean(), 1)
    
    kpi_col1.metric("Total Study Investment", f"{total_hours} Hours")
    kpi_col2.metric("Average Distraction Frequency", f"{avg_distract} per Session")
    kpi_col3.metric("Overall Focus Accuracy", f"{avg_focus} / 5.0")
    
    # 2. Main Analytical Visualizations Row
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Distribution of overall effort
        st.write("### ⏱️ Total Time Distribution")
        fig_effort = px.bar(
            df_active,
            x="Subject",
            y="Duration_Min",
            color="Subject",
            title="Total Combined Minutes Studied",
            color_discrete_sequence=COLOR_PALETTE
        )
        st.plotly_chart(fig_effort, use_container_width=True)
        
    with viz_col2:
        # Relationship analysis: Distractions vs Focus Rating
        st.write("### ⚡ Attention Friction Analysis")
        fig_scatter = px.scatter(
            df_active,
            x="Distractions",
            y="Focus_Rating",
            size="Duration_Min",
            color="Subject",
            title="The Impact of Distraction Events on Perceived Focus",
            color_discrete_sequence=COLOR_PALETTE
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    # 3. Peak Focus Hour Mapping Row
    st.write("### 🕒 Cognitive Window Time Analysis")
    hourly_performance = df_active.groupby("Hour")["Focus_Rating"].mean().reset_index()
    fig_time = px.bar(
        hourly_performance,
        x="Hour",
        y="Focus_Rating",
        color="Focus_Rating",
        color_continuous_scale=SEQUENTIAL_COLORS,
        title="Identifying Peak Daily Focus Windows (Highest Average Rating)"
    )
    st.plotly_chart(fig_time, use_container_width=True)

# ==========================================
# 5. DATA PORTABILITY (EXPORT & IMPORT BACKUPS)
# ==========================================
st.write("---")
st.subheader("💾 3. Keep & Manage Your Real Data Files")
st.write(format_text("Because Streamlit runs in-memory, you can download your logged history to your computer and upload it anytime to continue tracking where you left off."))

export_col, import_col = st.columns(2)

with export_col:
    # Convert active dataframe to CSV for dynamic export
    csv_data = df_active.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download FocusForge Database File (.csv)",
        data=csv_data,
        file_name="focusforge_database.csv",
        mime="text/csv"
    )

with import_col:
    # Allow students to upload their previously saved CSV files back in
    uploaded_file = st.file_uploader("📤 Restore Previous FocusForge File:", type=["csv"])
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            # Basic validation
            required_columns = ["Date", "Hour", "Subject", "Duration_Min", "Distractions", "Focus_Rating"]
            if all(col in uploaded_df.columns for col in required_columns):
                st.session_state.study_logs = uploaded_df
                st.success("Successfully imported data! All metrics charts updated.")
                # Refresh browser page to update values instantly
                st.rerun()
            else:
                st.error("Invalid database structure. File is missing standard FocusForge columns.")
        except Exception as e:
            st.error(f"Error parsing database file: {e}")
