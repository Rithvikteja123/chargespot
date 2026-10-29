"""
app.py
Main Entry Point & Home Dashboard for ChargeSpot.
Course: CSE494 - Intelligent NoSQL Databases.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from db.connection import check_connection, db
from services.analytics_service import get_network_kpis, get_connector_status_counts
from services.session_service import get_all_sessions
from services.station_service import get_all_stations
from styles import apply_custom_theme, render_badge

# Page configuration
st.set_page_config(
    page_title="ChargeSpot — EV Availability Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_theme()

# Sidebar branding & database status
with st.sidebar:
    st.markdown("### ⚡ **ChargeSpot**")
    st.markdown("*EV Availability & Analytics*")
    st.divider()

    is_connected = check_connection()
    if is_connected:
        st.success(f"● MongoDB Connected\n`{db.name}`", icon="🍃")
    else:
        st.error("✗ MongoDB Disconnected\nCheck local service", icon="🚨")

    st.markdown("---")
    st.markdown("**Academic Viva Navigation**")
    st.caption("1. Home: Network KPIs & Live Status\n2. Find a Station: Search & Filter\n3. Manage Stations: CRUD Operations\n4. Charging Sessions: Real-time Lifecycle\n5. Insights: Aggregations & ML")
    st.markdown("---")
    st.caption("CSE494 Individual Project")

# Main Page Header
col_header_left, col_header_right = st.columns([3, 1])
with col_header_left:
    st.markdown('<div class="hero-title">Find your next charge.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-tagline">“A little more charge, a little less waiting.” — Intelligent NoSQL EV Network Tracker</div>', unsafe_allow_html=True)

with col_header_right:
    st.markdown(
        f'<div style="text-align: right; padding-top: 0.5rem;">'
        f'{render_badge("operational" if is_connected else "out_of_service")}'
        f'<div style="font-size:0.8rem; color:#64748B; margin-top:4px;">Local Database: chargespot_db</div>'
        f'</div>',
        unsafe_allow_html=True
    )

if not is_connected:
    st.error("Cannot connect to MongoDB. Please make sure `mongod` is running on `mongodb://localhost:27017/` and reload.")
    st.stop()

# -------------------------------------------------------------
# 1. NETWORK METRIC CARDS
# -------------------------------------------------------------
kpis = get_network_kpis()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Stations</div>
        <div class="metric-value">{kpis['total_stations']}</div>
        <div class="metric-subtext">Across Punjab & CHD</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #10B981;">
        <div class="metric-title">Available Connectors</div>
        <div class="metric-value" style="color: #10B981;">{kpis['available_connectors']}</div>
        <div class="metric-subtext">Ready for charging</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #F59E0B;">
        <div class="metric-title">Occupied Connectors</div>
        <div class="metric-value" style="color: #D97706;">{kpis['occupied_connectors']}</div>
        <div class="metric-subtext">In active sessions</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #EF4444;">
        <div class="metric-title">Out of Service</div>
        <div class="metric-value" style="color: #DC2626;">{kpis['out_of_service_connectors']}</div>
        <div class="metric-subtext">Maintenance / Faulty</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #1B4332;">
        <div class="metric-title">Energy Delivered</div>
        <div class="metric-value">{kpis['total_energy_kwh']:,.1f}</div>
        <div class="metric-subtext">kWh across all sessions</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. LIVE AVAILABILITY CHART & RECENT ACTIVITY
# -------------------------------------------------------------
col_chart, col_recent = st.columns([1, 1.2])

with col_chart:
    st.subheader("⚡ Live Connector Availability")
    status_data = get_connector_status_counts()
    if status_data:
        df_status = pd.DataFrame(status_data)
        # Map nice labels
        df_status["Label"] = df_status["status"].str.replace("_", " ").str.title()
        
        color_map = {
            "Available": "#10B981",
            "Occupied": "#F59E0B",
            "Out Of Service": "#EF4444"
        }

        fig = px.pie(
            df_status,
            names="Label",
            values="count",
            hole=0.55,
            color="Label",
            color_discrete_map=color_map
        )
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No connector records found.")

with col_recent:
    st.subheader("⏱ Recent Charging Sessions")
    recent_sessions = get_all_sessions(limit=5)
    if recent_sessions:
        display_rows = []
        for s in recent_sessions:
            display_rows.append({
                "Session ID": s.get("session_id"),
                "Station": s.get("station_id"),
                "Plug": s.get("connector_id"),
                "Vehicle": s.get("vehicle_id"),
                "Energy (kWh)": s.get("energy_kwh", 0.0),
                "Status": s.get("status").replace("_", " ").title()
            })
        df_recent = pd.DataFrame(display_rows)
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.info("No session records found.")

st.divider()

# -------------------------------------------------------------
# 3. STATION NETWORK PREVIEW
# -------------------------------------------------------------
st.subheader("📍 Station Network Quick View")
stations = get_all_stations()

cols = st.columns(3)
for idx, st_doc in enumerate(stations[:6]):
    col = cols[idx % 3]
    with col:
        # Calculate availability for this station
        conns = st_doc.get("connectors", [])
        avail_count = sum(1 for c in conns if c.get("status") == "available")
        occ_count = sum(1 for c in conns if c.get("status") == "occupied")
        fault_count = sum(1 for c in conns if c.get("status") == "out_of_service")
        
        st.markdown(f"""
        <div class="station-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
                <span style="font-weight:700; color:#1B4332; font-size:1.05rem;">{st_doc.get('name')}</span>
                <span class="badge-speed">{st_doc.get('charging_speed_kw')} kW</span>
            </div>
            <div style="font-size:0.85rem; color:#64748B; margin-bottom:0.75rem;">
                📍 {st_doc.get('city')} — {st_doc.get('location', {}).get('area')}
            </div>
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap; font-size:0.8rem;">
                <span class="badge badge-available">🟢 {avail_count} Avail</span>
                <span class="badge badge-occupied">🟠 {occ_count} Busy</span>
                <span class="badge badge-out-of-service">🔴 {fault_count} Maint</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Viva / Academic Concept Callout
st.markdown("""
<div class="academic-callout">
    <strong>💡 CSE494 Academic Note — MongoDB Document Model Justification:</strong><br>
    Connectors are stored as an <em>embedded array of subdocuments</em> inside each station because connector counts are small (2-5) and are always retrieved together with the station details. Conversely, <em>charging sessions</em> are stored in a separate collection referenced by <code>station_id</code> because session history grows unbounded over time, avoiding the 16MB document size limit and enabling powerful multi-stage <code>$lookup</code> and <code>$group</code> aggregations.
</div>
""", unsafe_allow_html=True)
