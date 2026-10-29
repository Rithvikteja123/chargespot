"""
pages/3_Charging_Sessions.py
Charging session lifecycle management demonstrating business consistency rules:
- Start session: inserts session, locks connector to 'occupied'
- End session: updates session with energy and duration, unlocks connector back to 'available'
- Cancel session: safely aborts and frees connector
"""

from datetime import datetime
import streamlit as st
import pandas as pd
from services.session_service import (
    get_all_sessions, get_active_sessions, start_charging_session,
    end_charging_session, cancel_charging_session, delete_session
)
from services.station_service import get_all_stations, get_station_by_id
from styles import apply_custom_theme, render_badge

st.set_page_config(page_title="Charging Sessions — ChargeSpot", page_icon="⚡", layout="wide")
apply_custom_theme()

st.markdown('<div class="hero-title">Charging Sessions</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-tagline">Track active charging sessions, simulate plug-ins, and inspect historical energy delivery.</div>', unsafe_allow_html=True)

tab_active, tab_start, tab_history = st.tabs([
    "⚡ Active Sessions (Ongoing)",
    "🔌 Start New Session (Plug In)",
    "📜 Session History & Analytics"
])

# -------------------------------------------------------------
# TAB 1: ACTIVE SESSIONS
# -------------------------------------------------------------
with tab_active:
    st.subheader("Ongoing Charging Sessions (`status: 'in_progress'`)")
    st.caption("Ending an active session automatically frees the connector and recalculates energy consumption.")

    active_list = get_active_sessions()
    if not active_list:
        st.success("✅ No active charging sessions at the moment. All operational plugs are available!")
    else:
        st.markdown(f"**{len(active_list)} vehicle(s) currently charging across the network:**")
        
        for sess in active_list:
            sess_id = sess["session_id"]
            station = get_station_by_id(sess["station_id"])
            st_name = station["name"] if station else sess["station_id"]
            
            with st.container():
                st.markdown(f"""
                <div class="station-card" style="border-left: 4px solid #F59E0B;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:700; color:#1B4332; font-size:1.1rem;">Session {sess_id}</span>
                            <span style="margin-left:10px; color:#64748B;">Vehicle: <strong>{sess.get('vehicle_id')}</strong></span>
                            <div style="font-size:0.88rem; color:#64748B; margin-top:4px;">
                                📍 Station: <strong>{st_name}</strong> | Plug: <strong>{sess.get('connector_id')}</strong>
                            </div>
                        </div>
                        <div>
                            {render_badge('in_progress')}
                            <div style="font-size:0.8rem; color:#64748B; margin-top:4px; text-align:right;">
                                Started: {sess.get('started_at').strftime('%b %d, %H:%M') if isinstance(sess.get('started_at'), datetime) else sess.get('started_at')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_end, col_cancel = st.columns([2, 1])
                with col_end:
                    with st.form(f"end_form_{sess_id}"):
                        c_kwh, c_btn = st.columns([1.5, 1])
                        with c_kwh:
                            kwh_input = st.number_input(
                                "Energy Consumed (kWh) *",
                                min_value=0.1,
                                max_value=120.0,
                                value=24.5,
                                step=0.5,
                                key=f"kwh_{sess_id}"
                            )
                        with c_btn:
                            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                            end_submitted = st.form_submit_button("🏁 Complete & Free Plug")
                            if end_submitted:
                                ok, msg = end_charging_session(sess_id, kwh_input)
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                with col_cancel:
                    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                    if st.button("Cancel Session", key=f"cancel_{sess_id}"):
                        ok, msg = cancel_charging_session(sess_id)
                        if ok:
                            st.warning(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                st.divider()

# -------------------------------------------------------------
# TAB 2: START NEW SESSION
# -------------------------------------------------------------
with tab_start:
    st.subheader("Start a Demonstration Charging Session")
    st.caption("Enforces business rule: Connector must be 'available' and station must be 'operational'.")

    # Get operational stations that have at least one available connector
    all_stations = get_all_stations()
    eligible_stations = []
    for s in all_stations:
        if s.get("status") == "operational":
            avail_conns = [c["connector_id"] for c in s.get("connectors", []) if c.get("status") == "available"]
            if avail_conns:
                eligible_stations.append(s)

    if not eligible_stations:
        st.warning("No operational stations currently have available connectors. Free a connector first.")
    else:
        st_map = {f"{s['station_id']} — {s['name']} ({s['city']})": s for s in eligible_stations}
        chosen_label = st.selectbox("Select Station", list(st_map.keys()))
        chosen_station = st_map[chosen_label]

        # Available connectors for selected station
        free_conns = [c for c in chosen_station.get("connectors", []) if c.get("status") == "available"]
        conn_labels = {f"Plug {c['connector_id']} ({c['connector_type']}, {c['power_kw']} kW, ₹{c['price_per_kwh']}/kWh)": c['connector_id'] for c in free_conns}

        with st.form("start_session_form"):
            col_st1, col_st2 = st.columns(2)
            with col_st1:
                selected_conn_label = st.selectbox("Select Available Plug *", list(conn_labels.keys()))
                chosen_connector_id = conn_labels[selected_conn_label]
            with col_st2:
                vehicle_input = st.text_input("Vehicle Identifier *", value="EV-DEMO-01", placeholder="e.g. EV-NEXON-88").strip()

            submit_start = st.form_submit_button("🚀 Start Charging Session")
            if submit_start:
                if not vehicle_input:
                    st.error("Please enter a vehicle identifier.")
                else:
                    ok, msg, new_sid = start_charging_session(
                        station_id=chosen_station["station_id"],
                        connector_id=chosen_connector_id,
                        vehicle_id=vehicle_input
                    )
                    if ok:
                        st.success(f"✓ {msg}")
                        st.rerun()
                    else:
                        st.error(f"Cannot start session: {msg}")

# -------------------------------------------------------------
# TAB 3: SESSION HISTORY & ARCHIVE
# -------------------------------------------------------------
with tab_history:
    st.subheader("Charging Session History Log")
    
    filter_col1, filter_col2 = st.columns([1, 2])
    with filter_col1:
        hist_status = st.selectbox("Filter Status", ["All", "completed", "in_progress", "cancelled"])
    with filter_col2:
        search_veh = st.text_input("Filter by Vehicle or Session ID", placeholder="e.g. NEXON or SESS-1001").strip()

    history_records = get_all_sessions(limit=150, status_filter=hist_status)

    if search_veh:
        history_records = [
            r for r in history_records 
            if search_veh.lower() in r.get("vehicle_id", "").lower() or search_veh.lower() in r.get("session_id", "").lower()
        ]

    if history_records:
        hist_table = []
        for r in history_records:
            st_time = r.get("started_at")
            st_str = st_time.strftime("%Y-%m-%d %H:%M") if isinstance(st_time, datetime) else str(st_time)
            
            end_time = r.get("ended_at")
            end_str = end_time.strftime("%Y-%m-%d %H:%M") if isinstance(end_time, datetime) else ("—" if not end_time else str(end_time))

            # Duration calculation
            if isinstance(st_time, datetime) and isinstance(end_time, datetime):
                duration_min = round((end_time - st_time).total_seconds() / 60)
                dur_str = f"{duration_min} mins"
            else:
                dur_str = "Ongoing" if r.get("status") == "in_progress" else "—"

            hist_table.append({
                "Session ID": r.get("session_id"),
                "Station": r.get("station_id"),
                "Plug": r.get("connector_id"),
                "Vehicle": r.get("vehicle_id"),
                "Started At": st_str,
                "Ended At": end_str,
                "Duration": dur_str,
                "Energy (kWh)": r.get("energy_kwh", 0.0),
                "Status": r.get("status").title()
            })

        df_hist = pd.DataFrame(hist_table)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        # Session Deletion Demonstration
        st.markdown("##### 🗑️ Delete a Test Session Record (`delete_one`)")
        del_sess_id = st.selectbox("Select Session ID to Delete", [r["Session ID"] for r in hist_table])
        if st.button("Delete Selected Session Record"):
            del_ok, del_msg = delete_session(del_sess_id)
            if del_ok:
                st.success(del_msg)
                st.rerun()
            else:
                st.error(del_msg)
    else:
        st.info("No session records match your filter.")
