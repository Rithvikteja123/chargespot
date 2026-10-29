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
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main background */
    .stApp {
        background-color: #F8F9F5;
        color: #1E293B;
    }

    /* Top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Header styling */
    .hero-title {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1B4332;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }

    .hero-tagline {
        font-size: 1.05rem;
        color: #52796F;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }

    /* Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E8ECE9;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(27, 67, 50, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(27, 67, 50, 0.08);
    }

    .metric-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #1B4332;
    }

    .metric-subtext {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 0.2rem;
    }

    /* Station Card */
    .station-card {
        background: #FFFFFF;
        border: 1px solid #E8ECE9;
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }

    .station-card:hover {
        border-color: #A3C9A8;
        box-shadow: 0 4px 14px rgba(27, 67, 50, 0.08);
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: capitalize;
    }

    .badge-available {
        background-color: #E8F5E9;
        color: #1B5E20;
        border: 1px solid #C8E6C9;
    }

    .badge-occupied {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
    }

    .badge-out-of-service {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }

    .badge-operational {
        background-color: #E6F4EA;
        color: #137333;
    }

    .badge-speed {
        background-color: #EBF5FB;
        color: #1B4F72;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.2rem 0.5rem;
        font-size: 0.78rem;
    }

    /* Buttons */
    .stButton>button {
        background-color: #1B4332;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.25rem;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background-color: #2D6A4F;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.2);
    }

    /* Academic callout box */
    .academic-callout {
        background: #F0F4F1;
        border-left: 4px solid #2D6A4F;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #2D3748;
    }

    /* Sidebar style */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E8ECE9;
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
