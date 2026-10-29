"""
pages/1_Find_a_Station.py
Search and explore charging stations with multi-parameter filtering.
"""

import streamlit as st
import pandas as pd
from services.station_service import search_stations, get_unique_cities
from services.session_service import start_charging_session
from styles import apply_custom_theme, render_badge

st.set_page_config(page_title="Find a Station — ChargeSpot", page_icon="🔍", layout="wide")
apply_custom_theme()

st.markdown('<div class="hero-title">Find a Charging Station</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-tagline">Search real-time availability across fast-chargers and destination plugs.</div>', unsafe_allow_html=True)

# Filter Controls
with st.container():
    search_col, city_col, status_col, type_col = st.columns([2, 1, 1, 1])

    with search_col:
        search_query = st.text_input("🔍 Search by name or area", placeholder="e.g., Campus, GT Road, BMC...")

    with city_col:
        cities = ["All"] + get_unique_cities()
        selected_city = st.selectbox("📍 City", cities)

    with status_col:
        selected_status = st.selectbox("⚙️ Station Status", ["All", "operational", "maintenance", "closed"])

    with type_col:
        selected_type = st.selectbox("🔌 Connector Type", ["All", "CCS2", "Type 2", "CHAdeMO", "GB/T"])

    speed_col1, speed_col2 = st.columns([2, 2])
    with speed_col1:
        min_speed = st.slider("⚡ Minimum Charging Speed (kW)", min_value=0, max_value=150, value=0, step=10)

stations = search_stations(
    search_text=search_query,
    city=selected_city,
    status=selected_status,
    connector_type=selected_type,
    min_speed=min_speed
)

st.markdown(f"**Found {len(stations)} station(s) matching your criteria**")
st.markdown("<br>", unsafe_allow_html=True)

if not stations:
    st.info("No charging stations match your current filters. Try relaxing the search parameters.")
else:
    for st_doc in stations:
        station_id = st_doc["station_id"]
        conns = st_doc.get("connectors", [])
        avail_count = sum(1 for c in conns if c.get("status") == "available")
        occ_count = sum(1 for c in conns if c.get("status") == "occupied")
        maint_count = sum(1 for c in conns if c.get("status") == "out_of_service")

        with st.container():
            st.markdown(f"""
            <div class="station-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <span style="font-size:1.2rem; font-weight:700; color:#1B4332;">{st_doc['name']}</span>
                        <span style="color:#64748B; font-size:0.9rem; margin-left:8px;">({station_id})</span>
                        <div style="color:#64748B; font-size:0.88rem; margin-top:4px;">
                            📍 {st_doc.get('location', {}).get('address')}, {st_doc.get('city')}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge-speed">{st_doc.get('charging_speed_kw')} kW Rapid</span>
                        <div style="margin-top:6px;">{render_badge(st_doc.get('status', 'operational'))}</div>
                    </div>
                </div>
                <div style="margin-top:1rem; display:flex; gap:0.5rem; align-items:center;">
                    <span style="font-size:0.85rem; font-weight:600; color:#1E293B;">Connectors:</span>
                    <span class="badge badge-available">🟢 {avail_count} Available</span>
                    <span class="badge badge-occupied">🟠 {occ_count} Busy</span>
                    <span class="badge badge-out-of-service">🔴 {maint_count} Out of Service</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"View Connector Details & Start Session for {st_doc['name']}"):
                conn_display = []
                for c in conns:
                    conn_display.append({
                        "Connector ID": c.get("connector_id"),
                        "Standard": c.get("connector_type"),
                        "Power (kW)": c.get("power_kw"),
                        "Tariff (₹/kWh)": f"₹{c.get('price_per_kwh'):.2f}",
                        "Current Status": c.get("status").replace("_", " ").title()
                    })
                st.dataframe(pd.DataFrame(conn_display), use_container_width=True, hide_index=True)

                # Quick Session Launcher
                available_conns = [c["connector_id"] for c in conns if c.get("status") == "available"]
                if available_conns and st_doc.get("status") == "operational":
                    st.markdown("##### 🚀 Quick Demo: Plug in an EV here")
                    quick_col1, quick_col2, quick_col3 = st.columns([1, 1, 1])
                    with quick_col1:
                        selected_conn = st.selectbox(f"Select Plug ({station_id})", available_conns, key=f"plug_{station_id}")
                    with quick_col2:
                        quick_veh = st.text_input(f"Vehicle Tag", value="EV-DEMO-01", key=f"veh_{station_id}")
                    with quick_col3:
                        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                        if st.button("Start Charging Session", key=f"btn_{station_id}"):
                            ok, msg, sess_id = start_charging_session(station_id, selected_conn, quick_veh)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                elif st_doc.get("status") != "operational":
                    st.warning("Station is currently undergoing maintenance. Plugs unavailable.")
                else:
                    st.info("All plugs at this station are currently occupied or under maintenance.")
            st.markdown("<br>", unsafe_allow_html=True)
