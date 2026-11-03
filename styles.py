"""
styles.py
Custom CSS and design system tokens for ChargeSpot.

Color Palette:
- Primary: #1B4332 (Forest Green)
- Primary Accent: #2D6A4F
- Secondary Light: #52B788
- Background: #F8F9F5 (Warm off-white)
- Card Background: #FFFFFF
- Border: #E2E8F0
- Text Primary: #1E293B
- Text Muted: #64748B
- Available: #10B981 (Emerald)
- Occupied: #F59E0B (Amber)
- Out of Service: #EF4444 (Rose/Red)
"""

import streamlit as st

def apply_custom_theme():
    """Injects high-polish custom CSS styling into the Streamlit app."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #1E293B;
    }

    /* Main background */
    .stApp {
        background-color: #F8F9F5 !important;
        color: #1E293B !important;
    }

    /* Seamless top header */
    header[data-testid="stHeader"] {
        background-color: #F8F9F5 !important;
        border-bottom: 1px solid #E8ECE9 !important;
    }
    
    header[data-testid="stHeader"] * {
        color: #1E293B !important;
    }

    /* Top padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* Header styling */
    .hero-title {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #1B4332 !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.25rem !important;
    }

    .hero-tagline {
        font-size: 1.05rem !important;
        color: #52796F !important;
        font-weight: 500 !important;
        margin-bottom: 1.5rem !important;
    }

    /* Metric Cards */
    .metric-card {
        background: #FFFFFF !important;
        border: 1px solid #E8ECE9 !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        box-shadow: 0 2px 8px rgba(27, 67, 50, 0.04) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }

    .metric-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(27, 67, 50, 0.08) !important;
    }

    .metric-title {
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #64748B !important;
        font-weight: 600 !important;
        margin-bottom: 0.35rem !important;
    }

    .metric-value {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: #1B4332 !important;
    }

    .metric-subtext {
        font-size: 0.8rem !important;
        color: #64748B !important;
        margin-top: 0.2rem !important;
    }

    /* Station Card */
    .station-card {
        background: #FFFFFF !important;
        border: 1px solid #E8ECE9 !important;
        border-radius: 14px !important;
        padding: 1.4rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
    }

    .station-card:hover {
        border-color: #A3C9A8 !important;
        box-shadow: 0 4px 14px rgba(27, 67, 50, 0.08) !important;
    }

    /* Status Badges */
    .badge {
        display: inline-block !important;
        padding: 0.25rem 0.65rem !important;
        border-radius: 9999px !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        text-transform: capitalize !important;
    }

    .badge-available {
        background-color: #E8F5E9 !important;
        color: #1B5E20 !important;
        border: 1px solid #C8E6C9 !important;
    }

    .badge-occupied {
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        border: 1px solid #FDE68A !important;
    }

    .badge-out-of-service {
        background-color: #FEE2E2 !important;
        color: #991B1B !important;
        border: 1px solid #FECACA !important;
    }

    .badge-operational {
        background-color: #E6F4EA !important;
        color: #137333 !important;
        border: 1px solid #CEEAD6 !important;
    }

    .badge-speed {
        background-color: #EBF5FB !important;
        color: #1B4F72 !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 0.2rem 0.5rem !important;
        font-size: 0.78rem !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #1B4332 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background-color: #2D6A4F !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.2) !important;
    }

    /* Academic callout box */
    .academic-callout {
        background: #F0F4F1 !important;
        border-left: 4px solid #2D6A4F !important;
        padding: 1rem 1.25rem !important;
        border-radius: 0 8px 8px 0 !important;
        margin: 1rem 0 !important;
        font-size: 0.9rem !important;
        color: #2D3748 !important;
    }

    /* ======================================================== */
    /* HIGH-CONTRAST SIDEBAR STYLING (FIXES WASHED-OUT TEXT)     */
    /* ======================================================== */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] strong {
        color: #1E293B !important;
    }

    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {
        color: #475569 !important;
        font-weight: 500 !important;
    }

    /* Navigation Links in Sidebar */
    [data-testid="stSidebarNav"] ul {
        padding-top: 0.5rem !important;
    }

    [data-testid="stSidebarNav"] li a {
        padding: 0.6rem 0.85rem !important;
        border-radius: 10px !important;
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.15s ease-in-out !important;
    }

    [data-testid="stSidebarNav"] li a:hover {
        background-color: #F1F5F9 !important;
        color: #1B4332 !important;
    }

    [data-testid="stSidebarNav"] li a[aria-current="page"] {
        background-color: #E8F5E9 !important;
        color: #1B4332 !important;
        font-weight: 700 !important;
        border-left: 4px solid #10B981 !important;
    }

    [data-testid="stSidebarNav"] li a span {
        color: inherit !important;
    }

    /* Custom Table Container for crisp modern data displays */
    .custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        overflow: hidden;
        font-size: 0.88rem;
    }

    .custom-table th {
        background-color: #F8FAFC;
        color: #475569;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E2E8F0;
        text-align: left;
    }

    .custom-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #F1F5F9;
        color: #1E293B;
    }

    .custom-table tr:last-child td {
        border-bottom: none;
    }

    .custom-table tr:hover td {
        background-color: #F8FAFC;
    }

    /* Form input fields */
    .stTextInput input, .stSelectbox [data-baseweb="select"], .stNumberInput input {
        border-radius: 8px !important;
        border-color: #CBD5E1 !important;
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 1px #10B981 !important;
    }

    /* Headings in main content */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_badge(status):
    """Returns HTML for a status pill badge."""
    norm = status.lower().replace(" ", "_")
    if norm in ["available", "operational"]:
        css_class = "badge-available"
        dot = "🟢"
    elif norm in ["occupied", "in_progress"]:
        css_class = "badge-occupied"
        dot = "🟠"
    else:
        css_class = "badge-out-of-service"
        dot = "🔴"
    
    label = status.replace("_", " ").title()
    return f'<span class="badge {css_class}">{dot} {label}</span>'
