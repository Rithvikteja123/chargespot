"""
pages/4_Insights.py
Visual analytics driven by MongoDB Aggregation Pipelines
and explainable Machine Learning Busy Prediction.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from services.analytics_service import (
    get_energy_consumption_by_station,
    get_most_used_stations,
    get_session_status_breakdown,
    get_connector_type_distribution,
    get_connector_status_counts
)
from services.station_service import get_all_stations
from ml.busy_predictor import predictor
from styles import apply_custom_theme

st.set_page_config(page_title="Insights & ML — ChargeSpot", page_icon="📊", layout="wide")
apply_custom_theme()

st.markdown('<div class="hero-title">Analytics & Machine Learning</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-tagline">Academic demonstrations of MongoDB Aggregation Pipelines and Explainable Decision Tree Classification.</div>', unsafe_allow_html=True)

tab_agg, tab_ml = st.tabs([
    "📈 MongoDB Aggregation Analytics",
    "🤖 ML: Station Busy Predictor"
])

# -------------------------------------------------------------
# TAB 1: MONGODB AGGREGATION PIPELINES
# -------------------------------------------------------------
with tab_agg:
    st.subheader("1. Energy Consumption by Station")
    st.caption("Generated via `$match` (completed) ➔ `$group` (sum energy) ➔ `$lookup` (station details) ➔ `$project` ➔ `$sort`")

    energy_data = get_energy_consumption_by_station()
    if energy_data:
        df_energy = pd.DataFrame(energy_data)
        
        col_c1, col_t1 = st.columns([1.5, 1])
        with col_c1:
            fig_energy = px.bar(
                df_energy,
                x="total_energy_kwh",
                y="station_name",
                orientation="h",
                color="total_energy_kwh",
                color_continuous_scale="Greens",
                labels={"total_energy_kwh": "Total Energy (kWh)", "station_name": "Station Name"},
                title="Energy Delivered per Station (kWh)"
            )
            fig_energy.update_layout(
                yaxis=dict(autorange="reversed"),
                margin=dict(l=10, r=10, t=30, b=10),
                height=320,
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_energy, use_container_width=True)

        with col_t1:
            st.dataframe(
                df_energy[["station_id", "station_name", "city", "total_energy_kwh", "session_count"]],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No completed session data found.")

    st.divider()

    # Row 2: Most Used Stations & Connector Standards
    col_row2_left, col_row2_right = st.columns(2)

    with col_row2_left:
        st.subheader("2. Most Used Stations Ranking")
        st.caption("Generated via `$group` ➔ `$lookup` ➔ `$sort` (descending) ➔ `$limit: 8`")
        most_used_data = get_most_used_stations()
        if most_used_data:
            df_used = pd.DataFrame(most_used_data)
            fig_used = px.bar(
                df_used,
                x="station_name",
                y="session_count",
                color="session_count",
                color_continuous_scale="Teal",
                labels={"session_count": "Number of Sessions", "station_name": "Station"},
                title="Top Charging Hubs by Session Volume"
            )
            fig_used.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                height=300,
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_used, use_container_width=True)

    with col_row2_right:
        st.subheader("3. Connector Standards Distribution")
        st.caption("Generated via `$unwind: '$connectors'` ➔ `$group` by connector_type")
        types_data = get_connector_type_distribution()
        if types_data:
            df_types = pd.DataFrame(types_data)
            fig_types = px.pie(
                df_types,
                names="connector_type",
                values="count",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism,
                title="Plugs by Connector Standard"
            )
            fig_types.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_types, use_container_width=True)

    # Viva Aggregation Explanation Accordion
    with st.expander("📖 CSE494 Viva Reference: Explanation of MongoDB Aggregation Stages"):
        st.markdown("""
        - **`$match`**: Filters documents like an SQL `WHERE` clause. Used here to select only `status: "completed"` charging sessions.
        - **`$unwind`**: Deconstructs an array field from the input documents to output a document for each element. Used to break up the nested `connectors` array in each station into individual records.
        - **`$group`**: Groups input documents by a specified identifier expression and applies accumulator expressions (like `$sum`, `$avg`).
        - **`$lookup`**: Performs a left outer join to an unsharded collection in the same database to filter in documents from the "joined" collection. Used to enrich session station IDs with the station's actual human-readable name and city.
        - **`$project`**: Passes along the documents with the requested fields to the next stage in the pipeline (field renaming, `$round`, or exclusion).
        - **`$sort`**: Reorders documents by designated fields in ascending (1) or descending (-1) order.
        """)

# -------------------------------------------------------------
# TAB 2: MACHINE LEARNING BUSY PREDICTION
# -------------------------------------------------------------
with tab_ml:
    st.subheader("Station Congestion Predictor (Machine Learning)")
    st.markdown("""
    This explainable Machine Learning model uses scikit-learn's **`DecisionTreeClassifier`** to predict whether
    an EV charging station is likely to experience **High Congestion (Busy)** or **Normal / Available** demand
    based on temporal factors (hour of day, weekend vs. weekday) and physical station capacity (power, connector count).
    """)

    # Model Performance KPI Card
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Model Architecture", "DecisionTreeClassifier (Depth=4)")
    with m_col2:
        st.metric("Test Accuracy Score", f"{predictor.accuracy}%")
    with m_col3:
        st.metric("Dataset Split", f"{predictor.train_size} Train / {predictor.test_size} Test")

    st.markdown("""
    <div class="academic-callout">
        <strong>⚠️ Academic Disclaimer:</strong> This machine learning feature is a demonstration model trained on synthetic EV usage patterns. It predicts statistical likelihood of congestion and <strong>never overwrites</strong> actual real-time connector availability in MongoDB.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Interactive Congestion Simulation")
    
    stations = get_all_stations()
    st_options = {f"{s['station_id']} — {s['name']} ({s['city']})": s for s in stations}
    
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    with col_sim1:
        chosen_sim_label = st.selectbox("Select Station", list(st_options.keys()), key="ml_st_select")
        chosen_sim_station = st_options[chosen_sim_label]
        sim_speed = chosen_sim_station.get("charging_speed_kw", 50)
        sim_conns = len(chosen_sim_station.get("connectors", []))
        st.caption(f"Hardware Specs: **{sim_speed} kW**, **{sim_conns} connectors**")

    with col_sim2:
        sim_day = st.selectbox("Day of the Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], index=4)

    with col_sim3:
        sim_hour = st.slider("Hour of Day (24h)", min_value=0, max_value=23, value=18, format="%d:00")

    if st.button("🔮 Predict Station Congestion", type="primary"):
        prediction_result = predictor.predict(
            hour_of_day=sim_hour,
            day_name=sim_day,
            charging_speed_kw=sim_speed,
            total_connectors=sim_conns
        )

        st.markdown("---")
        res_col1, res_col2 = st.columns([1, 1.5])

        with res_col1:
            if prediction_result["is_busy"]:
                st.error(f"### ⚠️ {prediction_result['prediction_label']}")
            else:
                st.success(f"### 🟢 {prediction_result['prediction_label']}")
            
            st.write(f"**Predicted Congestion Probability:** {prediction_result['probability_busy']}%")
            st.progress(prediction_result['probability_busy'] / 100.0)

        with res_col2:
            st.markdown("##### 🔍 Explainable Decision Logic")
            st.info(f"**Key Drivers:** {prediction_result['explanation']}")
            st.caption("Decision path: Evaluates whether the requested time coincides with morning/evening commuting peaks, weekend intercity travel spikes, and balances against station connector capacity.")
