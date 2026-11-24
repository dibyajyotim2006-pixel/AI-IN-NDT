import streamlit as st
import os
import pandas as pd

# Set page configuration must be first Streamlit command
st.set_page_config(
    page_title="NDT Intelligence | AI Concrete Assessment",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Industrial Dark Navy CSS Theme
st.markdown("""
<style>
    /* Dark Navy Core Background */
    .stApp {
        background-color: #0B132B;
        color: #F8FAFC;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Top Header Bar */
    header[data-testid="stHeader"] {
        background-color: rgba(11, 19, 43, 0.9);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    /* Card Styles */
    .metric-card {
        background: linear-gradient(145deg, #1E293B 0%, #162032 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #38BDF8;
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #94A3B8;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 4px;
    }
    
    /* Form Inputs and Selectors */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #0284C7 0%, #00F2FE 100%) !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #1E293B !important;
        color: #38BDF8 !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1E293B !important;
        border-radius: 6px !important;
        color: #E2E8F0 !important;
    }
    
    /* Radio buttons in sidebar */
    .stRadio > div {
        gap: 6px;
    }

    /* Dataframe tables */
    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# Import components
from components.dashboard import render_dashboard
from components.predictor import render_predictor
from components.database import render_database
from components.analytics import render_analytics
from components.reports import render_reports
from utils.storage import init_db

# Initialize database on startup
init_db()

# Sidebar Navigation & System Information
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 15px 0; border-bottom: 1px solid #1E293B; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background: linear-gradient(135deg, #0284C7 0%, #00F2FE 100%); width: 38px; height: 38px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">
                🏗️
            </div>
            <div>
                <h2 style="margin: 0; color: #FFFFFF; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.3px;">
                    NDT INTELLIGENCE
                </h2>
                <div style="color: #38BDF8; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.5px;">
                    AI CONCRETE ASSESSMENT
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_selection = st.radio(
        "SYSTEM NAVIGATION",
        options=[
            "📊 Executive Dashboard",
            "🧠 AI Strength Predictor",
            "🗄️ Sample Database",
            "📈 Analytics & Visualizations",
            "📑 PDF Report Generator"
        ],
        index=0
    )

    st.markdown("---")

    # Neural Network System Status Pill
    st.markdown("""
    <div style="background-color: #1E293B; border-radius: 8px; border: 1px solid #334155; padding: 14px 16px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">AI CORE STATUS</span>
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #10B981; box-shadow: 0 0 8px #10B981;"></span>
        </div>
        <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">
            ANN 6-6-1 Operational
        </div>
        <div style="font-size: 0.75rem; color: #38BDF8; margin-top: 2px;">
            Sigmoid Hidden | Linear Output
        </div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #334155; font-size: 0.72rem; color: #94A3B8; line-height: 1.3;">
            • Model Correlation R: <strong>0.9966</strong><br/>
            • Benchmark Target: <strong>0.99486</strong><br/>
            • SonReb Calibration Active
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Engineering Standard References
    st.markdown("""
    <div style="font-size: 0.72rem; color: #64748B; padding: 0 5px; line-height: 1.4;">
        <strong>Reference Standards:</strong><br/>
        • IS 13311 (Part 1): UPV Testing<br/>
        • IS 13311 (Part 2): Rebound Hammer<br/>
        • ASTM C805 & C597 / RILEM SonReb<br/>
        • Kiran IDP Concrete Assessment Spec
    </div>
    """, unsafe_allow_html=True)

# Main Content Routing
if "Executive Dashboard" in nav_selection:
    render_dashboard()
elif "AI Strength Predictor" in nav_selection:
    render_predictor()
elif "Sample Database" in nav_selection:
    render_database()
elif "Analytics" in nav_selection:
    render_analytics()
elif "PDF Report Generator" in nav_selection:
    render_reports()
