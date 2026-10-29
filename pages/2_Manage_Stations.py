"""
pages/2_Manage_Stations.py
Station management interface demonstrating full MongoDB CRUD operations:
- CREATE: insert_one() with client and collection-level $jsonSchema validation
- READ: find() and find_one()
- UPDATE: update_one() for station metadata and connector status ($ operator)
- DELETE: delete_one() with active session integrity guard
"""

from datetime import datetime
import streamlit as st
import pandas as pd
from services.station_service import (
    get_all_stations, get_station_by_id, create_station,
    update_station, update_connector_status, delete_station
)
from styles import apply_custom_theme, render_badge

st.set_page_config(page_title="Manage Stations — ChargeSpot", page_icon="⚙️", layout="wide")
apply_custom_theme()

st.markdown('<div class="hero-title">Station Management</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-tagline">Admin control panel for adding, updating, and removing station records.</div>', unsafe_allow_html=True)

tab_view, tab_add, tab_edit, tab_delete = st.tabs([
    "📋 All Stations (Read)",
    "➕ Add Station (Create)",
    "✏️ Edit & Availability (Update)",
    "🗑️ Delete Station (Delete)"
])

# -------------------------------------------------------------
# TAB 1: READ ALL STATIONS
# -------------------------------------------------------------
with tab_view:
    st.subheader("Current Stations in `chargespot_db.stations`")
    all_stations = get_all_stations()

    if all_stations:
        summary_rows = []
        for s in all_stations:
            conns = s.get("connectors", [])
            summary_rows.append({
                "Station ID": s.get("station_id"),
                "Name": s.get("name"),
                "City": s.get("city"),
                "Speed (kW)": s.get("charging_speed_kw"),
                "Connectors": len(conns),
                "Available": sum(1 for c in conns if c.get("status") == "available"),
                "Occupied": sum(1 for c in conns if c.get("status") == "occupied"),
                "Out of Service": sum(1 for c in conns if c.get("status") == "out_of_service"),
                "Status": s.get("status").title()
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No stations currently stored in the database.")

# -------------------------------------------------------------
# TAB 2: CREATE STATION (insert_one)
# -------------------------------------------------------------
with tab_add:
    st.subheader("Add a New EV Charging Station")
    st.caption("Demonstrates PyMongo `insert_one()` validated by MongoDB's `$jsonSchema` engine.")

    with st.form("add_station_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("Station ID *", placeholder="e.g. CS011").strip()
            new_name = st.text_input("Station Name *", placeholder="e.g. Sector 22 Fast Hub").strip()
            new_city = st.text_input("City *", placeholder="e.g. Chandigarh").strip()
            new_area = st.text_input("Area / Locality *", placeholder="e.g. Sector 22 Market").strip()

        with col2:
            new_address = st.text_input("Full Address *", placeholder="e.g. Near Bus Stand, Sector 22").strip()
            new_speed = st.number_input("Max Charging Speed (kW) *", min_value=1, max_value=350, value=60)
            new_status = st.selectbox("Operational Status *", ["operational", "maintenance", "closed"])
            num_connectors = st.selectbox("Number of Plugs to Add", [2, 3, 4], index=1)

        st.markdown("##### Configure Connectors")
        connectors_data = []
        c_cols = st.columns(num_connectors)
        for i in range(num_connectors):
            with c_cols[i]:
                st.markdown(f"**Plug C{i+1}**")
                c_type = st.selectbox(f"Standard C{i+1}", ["CCS2", "Type 2", "CHAdeMO", "GB/T"], key=f"add_ctype_{i}")
                c_power = st.number_input(f"Power (kW) C{i+1}", min_value=1.0, max_value=350.0, value=float(new_speed), key=f"add_cpow_{i}")
                c_price = st.number_input(f"Tariff (₹/kWh) C{i+1}", min_value=0.0, max_value=50.0, value=15.0, key=f"add_cprc_{i}")
                c_stat = st.selectbox(f"Status C{i+1}", ["available", "occupied", "out_of_service"], key=f"add_cstat_{i}")
                connectors_data.append({
                    "connector_id": f"C{i+1}",
                    "connector_type": c_type,
                    "power_kw": float(c_power),
                    "price_per_kwh": float(c_price),
                    "status": c_stat
                })

        submit_add = st.form_submit_button("Save Station to MongoDB")
        if submit_add:
            # Application-level validation
            if not new_id or not new_name or not new_city or not new_area or not new_address:
                st.error("Please fill in all required fields marked with *.")
            else:
                station_doc = {
                    "station_id": new_id,
                    "name": new_name,
                    "city": new_city,
                    "location": {
                        "city": new_city,
                        "area": new_area,
                        "address": new_address
                    },
                    "connector_type": connectors_data[0]["connector_type"],
                    "charging_speed_kw": int(new_speed),
                    "status": new_status,
                    "created_at": datetime.now(),
                    "connectors": connectors_data
                }
                success, msg = create_station(station_doc)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(f"Failed to add station: {msg}")

# -------------------------------------------------------------
# TAB 3: UPDATE STATION & AVAILABILITY (update_one)
# -------------------------------------------------------------
with tab_edit:
    st.subheader("Edit Station & Connector Availability")
    st.caption("Demonstrates `update_one()` with the `$set` and `connectors.$.status` array positional operator.")

    station_list = get_all_stations()
    if station_list:
        st_options = {f"{s['station_id']} — {s['name']} ({s['city']})": s['station_id'] for s in station_list}
        selected_label = st.selectbox("Select Station to Edit", list(st_options.keys()))
        target_st_id = st_options[selected_label]
        target_station = get_station_by_id(target_st_id)

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("##### 📝 Update Station Metadata")
            with st.form("edit_station_form"):
                edit_name = st.text_input("Station Name", value=target_station.get("name", ""))
                edit_speed = st.number_input("Max Speed (kW)", min_value=1, max_value=350, value=int(target_station.get("charging_speed_kw", 50)))
                edit_status = st.selectbox("Status", ["operational", "maintenance", "closed"],
                                           index=["operational", "maintenance", "closed"].index(target_station.get("status", "operational")))
                submit_edit = st.form_submit_button("Update Station Details")
                if submit_edit:
                    ok, msg = update_station(target_st_id, {
                        "name": edit_name,
                        "charging_speed_kw": edit_speed,
                        "status": edit_status
                    })
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with col_right:
            st.markdown("##### 🔌 Manage Individual Connector Status")
            st.caption("Toggle availability directly in the database.")
            for c in target_station.get("connectors", []):
                cid = c["connector_id"]
                current_cstatus = c.get("status", "available")
                status_options = ["available", "occupied", "out_of_service"]
                
                c_col1, c_col2 = st.columns([1.5, 1])
                with c_col1:
                    st.write(f"**Plug {cid}** ({c.get('connector_type')}, {c.get('power_kw')} kW)")
                    st.markdown(render_badge(current_cstatus), unsafe_allow_html=True)
                with c_col2:
                    new_cstat = st.selectbox(f"Set Status {cid}", status_options,
                                            index=status_options.index(current_cstatus),
                                            key=f"toggle_{target_st_id}_{cid}")
                    if new_cstat != current_cstatus:
                        if st.button(f"Save {cid}", key=f"btn_save_{target_st_id}_{cid}"):
                            ok, msg = update_connector_status(target_st_id, cid, new_cstat)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                st.divider()
    else:
        st.info("No stations found.")

# -------------------------------------------------------------
# TAB 4: DELETE STATION (delete_one)
# -------------------------------------------------------------
with tab_delete:
    st.subheader("Delete a Station")
    st.caption("Demonstrates `delete_one()` with referential integrity guard to protect active sessions.")

    if station_list:
        del_options = {f"{s['station_id']} — {s['name']} ({s['city']})": s['station_id'] for s in station_list}
        del_label = st.selectbox("Select Station to Delete", list(del_options.keys()), key="del_station_select")
        del_st_id = del_options[del_label]
        
        st.warning(f"⚠️ Warning: You are about to delete **{del_label}**.")
        confirm_check = st.checkbox(f"I understand that deleting {del_st_id} is permanent.")

        if st.button("Delete Station Record", type="primary", disabled=not confirm_check):
            ok, msg = delete_station(del_st_id)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(f"Cannot delete: {msg}")
    else:
        st.info("No stations to delete.")
