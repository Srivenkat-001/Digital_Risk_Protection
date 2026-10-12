"""
BrandPhantom: AI-Powered Digital Risk Protection Platform.
Main Streamlit application entry point.
"""

import streamlit as st

from config.logging_config import logger
from config.settings import settings
from db.models.organization import Organization
from db.session import get_db, init_db
from seed.demo_data import seed_demo_environment
from ui.navigation import dispatch_page, render_login_view
from ui.theme import apply_theme

# Page configuration
st.set_page_config(
    page_title=f"{settings.APP_NAME} | Digital Risk Protection",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply cybersecurity dark theme
apply_theme()

# Initialize database schema
init_db()

# Auto-seed demo environment on initial run if empty
with get_db() as db:
    org_count = db.query(Organization).count()
    if org_count == 0 and settings.DEMO_MODE_ENABLED:
        logger.info("Empty database detected. Auto-seeding initial NovaPay demo environment...")
        seed_demo_environment(db)

# Session state initialization
if "user" not in st.session_state:
    st.session_state["user"] = None
if "org" not in st.session_state:
    st.session_state["org"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"
if "selected_brand_id" not in st.session_state:
    st.session_state["selected_brand_id"] = "all"

# Dispatch view
with get_db() as db:
    if st.session_state["user"] is None:
        render_login_view(db)
    else:
        dispatch_page(db)
