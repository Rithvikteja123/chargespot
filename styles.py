"""
styles.py
High-Impact EV Fleet Operations Command Center Theme for ChargeSpot.
Features:
- Bespoke Floating Glassmorphic Top Navbar with Live Telemetry Pulse
- Ambient Cyber-Emerald & Slate Palette (#090D16, #111827, #10B981)
- Physical Connector Plug Visualizers
- Hidden Streamlit Clutter (No default Deploy / Toolbar)
"""

import streamlit as st

def apply_custom_theme():
    """Injects high-impact EV Command Center CSS styling."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #F1F5F9;
    }

    /* Hide Streamlit Default Header Clutter */
    .stDeployButton, #MainMenu, footer, [data-testid="stToolbar"], div[data-testid="stDecoration"] {
        display: none !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 1.2rem !important;
    }

    /* Ambient Cyber-Emerald Background */
    .stApp {
        background: radial-gradient(circle at 12% 10%, rgba(16, 185, 129, 0.09) 0%, transparent 35%),
                    radial-gradient(circle at 88% 80%, rgba(6, 182, 212, 0.07) 0%, transparent 40%),
                    #090D16 !important;
        color: #F1F5F9 !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 1280px !important;
    }

    /* ======================================================== */
    /* BESPOKE FLOATING TOP NAVBAR                               */
    /* ======================================================== */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(17, 24, 39, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 0.85rem 1.4rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 35px -5px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-logo {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
        text-shadow: 0 0 16px rgba(16, 185, 129, 0.5);
    }

    .brand-logo span.bolt {
        color: #10B981;
        font-size: 1.4rem;
    }

    .brand-meta {
        display: flex;
        flex-direction: column;
    }

    .brand-sub {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .pulse-badge {
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.28);
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        letter-spacing: 0.04em;
    }

    .pulse-dot {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10B981;
        animation: pulse-ring 2s infinite ease-in-out;
    }

    @keyframes pulse-ring {
        0% { transform: scale(0.95); opacity: 1; }
        50% { transform: scale(1.35); opacity: 0.4; }
        100% { transform: scale(0.95); opacity: 1; }
    }

    .nav-pills {
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba(10, 14, 23, 0.6);
        padding: 5px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .nav-link-btn {
        color: #94A3B8 !important;
        text-decoration: none !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        border-radius: 8px !important;
        transition: all 0.15s ease-in-out !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .nav-link-btn:hover {
        color: #FFFFFF !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }

    .nav-link-btn.active {
        color: #FFFFFF !important;
        background: #10B981 !important;
        box-shadow: 0 0 16px rgba(16, 185, 129, 0.4) !important;
    }

    .nav-status {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .mongo-pill {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34D399;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ======================================================== */
    /* LIVE TELEMETRY TICKER BANNER                             */
    /* ======================================================== */
    .telemetry-ticker {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-left: 4px solid #10B981;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.82rem;
        color: #94A3B8;
    }

    .telemetry-ticker strong {
        color: #FFFFFF;
    }

    /* ======================================================== */
    /* GLASSMORPHIC METRIC CARDS                                */
    /* ======================================================== */
    .metric-card {
        background: rgba(17, 24, 39, 0.7) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.3rem 1.1rem !important;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.45) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }

    .metric-card:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(16, 185, 129, 0.4) !important;
        box-shadow: 0 12px 30px -6px rgba(16, 185, 129, 0.2) !important;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10B981, #06B6D4);
        opacity: 0.8;
    }

    .metric-title {
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #94A3B8 !important;
        font-weight: 700 !important;
        margin-bottom: 0.35rem !important;
    }

    .metric-value {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .metric-subtext {
        font-size: 0.75rem !important;
        color: #64748B !important;
        margin-top: 0.25rem !important;
        font-weight: 500 !important;
    }

    /* Station Card */
    .station-card {
        background: rgba(17, 24, 39, 0.75) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.4rem !important;
        margin-bottom: 1.1rem !important;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.45) !important;
        transition: all 0.2s ease !important;
    }

    .station-card:hover {
        border-color: #10B981 !important;
        box-shadow: 0 12px 30px -6px rgba(16, 185, 129, 0.25) !important;
        transform: translateY(-2px) !important;
    }

    /* Physical Connector Plug Visualizer */
    .connector-pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 4px 10px;
        margin: 3px 4px 3px 0;
        font-size: 0.78rem;
        font-weight: 600;
        color: #E2E8F0;
    }

    /* Badges */
    .badge {
        display: inline-flex !important;
        align-items: center !important;
        gap: 5px !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 9999px !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        text-transform: capitalize !important;
    }

    .badge-available {
        background-color: rgba(16, 185, 129, 0.15) !important;
        color: #34D399 !important;
        border: 1px solid rgba(16, 185, 129, 0.35) !important;
    }

    .badge-occupied {
        background-color: rgba(245, 158, 11, 0.15) !important;
        color: #FBBF24 !important;
        border: 1px solid rgba(245, 158, 11, 0.35) !important;
    }

    .badge-out-of-service {
        background-color: rgba(239, 68, 68, 0.15) !important;
        color: #F87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.35) !important;
    }

    .badge-speed {
        background-color: rgba(6, 182, 212, 0.15) !important;
        color: #38BDF8 !important;
        border: 1px solid rgba(6, 182, 212, 0.3) !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        padding: 0.2rem 0.55rem !important;
        font-size: 0.75rem !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Custom Futuristic Glass Table */
    .custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        overflow: hidden;
        font-size: 0.88rem;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.45);
    }

    .custom-table th {
        background-color: rgba(15, 23, 42, 0.9);
        color: #94A3B8;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        padding: 0.85rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        text-align: left;
    }

    .custom-table td {
        padding: 0.85rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        color: #E2E8F0;
    }

    .custom-table tr:last-child td {
        border-bottom: none;
    }

    .custom-table tr:hover td {
        background-color: rgba(255, 255, 255, 0.04);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.55rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
    }

    /* Form input fields */
    .stTextInput input, .stSelectbox [data-baseweb="select"], .stNumberInput input {
        border-radius: 10px !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        color: #F8FAFC !important;
        background-color: rgba(15, 23, 42, 0.8) !important;
    }

    /* Sidebar Clean Dark Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    /* Headings in main content */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_top_navbar(active_page="Home"):
    """Renders a bespoke, high-polish horizontal top navigation bar across all pages."""
    pages = [
        ("Home", "/", "🏠 Dashboard"),
        ("Find a Station", "/Find_a_Station", "🔍 Find Station"),
        ("Manage Stations", "/Manage_Stations", "⚙️ Manage"),
        ("Charging Sessions", "/Charging_Sessions", "⚡ Sessions"),
        ("Insights", "/Insights", "📊 Insights & ML"),
    ]
    
    pills_html = ""
    for name, route, label in pages:
        is_active = (active_page.lower() == name.lower())
        active_class = "active" if is_active else ""
        pills_html += f'<a href="{route}" target="_self" class="nav-link-btn {active_class}">{label}</a>'

    navbar_html = f"""
    <div class="top-navbar">
        <div class="nav-brand">
            <div class="brand-logo">
                <span class="bolt">⚡</span> CHARGESPOT
            </div>
            <div class="brand-meta">
                <span class="brand-sub">EV Command Center</span>
            </div>
            <span class="pulse-badge"><span class="pulse-dot"></span> LIVE TELEMETRY</span>
        </div>
        <div class="nav-pills">
            {pills_html}
        </div>
        <div class="nav-status">
            <span class="mongo-pill">🍃 MongoDB 7.0 Active</span>
        </div>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

def render_badge(status):
    """Returns HTML for a status pill badge."""
    norm = status.lower().replace(" ", "_")
    if norm in ["available", "operational", "completed"]:
        css_class = "badge-available"
        dot = "🟢"
    elif norm in ["occupied", "in_progress", "active"]:
        css_class = "badge-occupied"
        dot = "🟠"
    elif norm in ["cancelled"]:
        css_class = "badge-speed"
        dot = "⚪"
    else:
        css_class = "badge-out-of-service"
        dot = "🔴"
    
    label = status.replace("_", " ").title()
    return f'<span class="badge {css_class}">{dot} {label}</span>'
