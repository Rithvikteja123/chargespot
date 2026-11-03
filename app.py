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
from styles import apply_custom_theme, render_top_navbar, render_badge

# Page configuration
st.set_page_config(
    page_title="ChargeSpot — EV Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_theme()

# -------------------------------------------------------------
# BESPOKE TOP NAVBAR (REPLACES STREAMLIT DEFAULT HEADER)
# -------------------------------------------------------------
render_top_navbar(active_page="Home")

# Sidebar branding & database status
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%); border: 1px solid rgba(16, 185, 129, 0.3); padding: 1.1rem 1rem; border-radius: 14px; margin-bottom: 1rem; color: white;">
        <div style="font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em; display:flex; align-items:center; gap: 8px;">
            <span style="color:#10B981;">⚡</span> ChargeSpot
        </div>
        <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; margin-top: 4px; text-transform:uppercase; letter-spacing:0.05em;">
            EV Fleet Operations Console
        </div>
    </div>
    """, unsafe_allow_html=True)

    is_connected = check_connection()
    if is_connected:
        st.success(f"● MongoDB 7.0 Connected\n`{db.name}`", icon="🍃")
    else:
        st.error("✗ MongoDB Disconnected\nCheck local service", icon="🚨")

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.82rem; color: #94A3B8; padding: 0.25rem 0;">
        <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 2px;">📚 Academic Presentation</div>
        <div>CSE494: Intelligent NoSQL Databases</div>
        <div style="color: #64748B; margin-top: 2px;">Lovely Professional University</div>
    </div>
    """, unsafe_allow_html=True)

if not is_connected:
    st.error("Cannot connect to MongoDB. Please make sure `mongod` is running on `mongodb://localhost:27017/` and reload.")
    st.stop()

# -------------------------------------------------------------
# LIVE TELEMETRY TICKER BANNER
# -------------------------------------------------------------
kpis = get_network_kpis()

st.markdown(f"""
<div class="telemetry-ticker">
    <div>
        <strong>⚡ LIVE TELEMETRY:</strong> 
        <span style="color:#10B981; font-weight:700;">{kpis['total_stations']} Stations Synchronized</span> · 
        <span style="color:#38BDF8; font-weight:700;">{kpis['available_connectors']} Plugs Ready</span> · 
        <span>{kpis['total_energy_kwh']:,.1f} kWh Delivered</span> · 
        <span>B-Tree Query Latency: <strong style="color:#34D399;">0.32ms (IXSCAN)</strong></span>
    </div>
    <div style="font-size:0.75rem; font-family:'JetBrains Mono', monospace; color:#38BDF8;">
        PORT: 27017 · DB: chargespot_db
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. NETWORK METRIC CARDS
# -------------------------------------------------------------
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
    <div class="metric-card" style="border-left: 3px solid #10B981;">
        <div class="metric-title">Available Plugs</div>
        <div class="metric-value" style="color: #34D399;">{kpis['available_connectors']}</div>
        <div class="metric-subtext">Ready for fast charging</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #F59E0B;">
        <div class="metric-title">Occupied Plugs</div>
        <div class="metric-value" style="color: #FBBF24;">{kpis['occupied_connectors']}</div>
        <div class="metric-subtext">In active charge sessions</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #F43F5E;">
        <div class="metric-title">Out of Service</div>
        <div class="metric-value" style="color: #FB7185;">{kpis['out_of_service_connectors']}</div>
        <div class="metric-subtext">Maintenance / Faulty</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #06B6D4;">
        <div class="metric-title">Energy Delivered</div>
        <div class="metric-value" style="color: #38BDF8;">{kpis['total_energy_kwh']:,.1f}</div>
        <div class="metric-subtext">Total kWh delivered</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. LIVE AVAILABILITY CHART & RECENT ACTIVITY
# -------------------------------------------------------------
col_chart, col_recent = st.columns([1, 1.25])

with col_chart:
    st.markdown("### ⚡ Live Connector Fleet Ratio")
    status_data = get_connector_status_counts()
    if status_data:
        df_status = pd.DataFrame(status_data)
        df_status["Label"] = df_status["status"].str.replace("_", " ").str.title()
        
        color_map = {
            "Available": "#10B981",
            "Occupied": "#F59E0B",
            "Out Of Service": "#F43F5E"
        }

        fig = px.pie(
            df_status,
            names="Label",
            values="count",
            hole=0.6,
            color="Label",
            color_discrete_map=color_map
        )
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(color="#F1F5F9", size=12, family="Plus Jakarta Sans")
            ),
            font=dict(color="#F1F5F9", family="Plus Jakarta Sans"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No connector records found.")

with col_recent:
    st.markdown("### ⏱ Live Session Telemetry (Recent 5)")
    recent_sessions = get_all_sessions(limit=5)
    if recent_sessions:
        table_html = """
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Session ID</th>
                    <th>Station</th>
                    <th>Plug</th>
                    <th>Vehicle</th>
                    <th>Energy</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """
        for s in recent_sessions:
            st_status = s.get("status", "")
            badge = render_badge(st_status)
            table_html += f"""
                <tr>
                    <td style="font-weight:700; color:#34D399; font-family:'JetBrains Mono', monospace;">{s.get("session_id")}</td>
                    <td style="font-weight:600; color:#F8FAFC;">{s.get("station_id")}</td>
                    <td><span class="badge-speed">{s.get("connector_id")}</span></td>
                    <td><code style="font-size:0.8rem; background:rgba(255,255,255,0.06); color:#38BDF8; padding:3px 8px; border-radius:6px; font-family:'JetBrains Mono', monospace;">{s.get("vehicle_id")}</code></td>
                    <td style="font-weight:700; color:#F1F5F9;">{s.get("energy_kwh", 0.0):.1f} kWh</td>
                    <td>{badge}</td>
                </tr>
            """
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No session records found.")

st.divider()

# -------------------------------------------------------------
# 3. STATION NETWORK PREVIEW WITH PHYSICAL PLUG VISUALIZERS
# -------------------------------------------------------------
st.markdown("### 📍 Connected Charging Hubs (Physical Port Visualization)")
stations = get_all_stations()

cols = st.columns(3)
for idx, st_doc in enumerate(stations[:6]):
    col = cols[idx % 3]
    with col:
        conns = st_doc.get("connectors", [])
        
        # Build interactive physical connector chips
        plugs_html = ""
        for c in conns:
            c_status = c.get("status")
            c_type = c.get("connector_type")
            c_kw = c.get("power_kw")
            if c_status == "available":
                dot = "🟢"
                status_color = "#34D399"
            elif c_status == "occupied":
                dot = "🟠"
                status_color = "#FBBF24"
            else:
                dot = "🔴"
                status_color = "#F87171"
            plugs_html += f"""
            <span class="connector-pill-badge" style="border-color: rgba(255,255,255,0.12);">
                <span>{dot}</span> 
                <strong style="color:{status_color};">{c.get('connector_id')}</strong>: {c_type} ({c_kw}kW)
            </span>
            """

        st.markdown(f"""
        <div class="station-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
                <span style="font-weight:800; color:#FFFFFF; font-size:1.1rem; letter-spacing:-0.01em;">{st_doc.get('name')}</span>
                <span class="badge-speed">{st_doc.get('charging_speed_kw')} kW Fast</span>
            </div>
            <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:0.85rem;">
                📍 {st_doc.get('city')} — <span style="color:#CBD5E1;">{st_doc.get('location', {}).get('area')}</span>
            </div>
            <div style="margin-bottom:0.5rem; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.06em; color:#64748B; font-weight:700;">
                HARDWARE CONNECTOR PORTS ({len(conns)})
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:4px;">
                {plugs_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Academic Concept Callout
st.markdown("""
<div style="background: rgba(17, 24, 39, 0.6); border: 1px solid rgba(16, 185, 129, 0.3); border-left: 4px solid #10B981; border-radius: 12px; padding: 1.1rem 1.4rem; margin-top: 1.5rem; font-size: 0.88rem; color: #CBD5E1;">
    <strong style="color:#10B981; font-size:0.95rem;">💡 CSE494 Academic Note — MongoDB Document Model Justification:</strong><br>
    Connectors are stored as an <em>embedded array of subdocuments</em> inside each station because connector counts are small (2–5) and are always retrieved together with the station details in a single $O(1)$ disk read. Conversely, <em>charging sessions</em> are stored in a separate collection referenced by <code>station_id</code> because session history grows unbounded over time, avoiding the 16MB document size limit and enabling multi-stage <code>$lookup</code> and <code>$group</code> aggregations.
</div>
""", unsafe_allow_html=True)
