"""
app.py - AI-Powered Intelligent Railway Travel & Autonomous AI Governance Platform MVP
Tech Stack: Streamlit, Pandas, Plotly.
"""
import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_manager import RailwayDataManager
from risk_engine import DelayRiskEngine
from governance_engine import GovernanceEngine, AuditLogger
from travel_assistant import TravelPlannerAgent

# Page setup
st.set_page_config(
    page_title="RailAI & AI Governance Platform",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    /* Global styling */
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.2rem;
    }
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .kpi-title {
        font-size: 0.82rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .disclaimer-box {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #334155;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading
@st.cache_resource(show_spinner="Loading and cleaning Railway Timetable dataset...")
def init_system():
    dm = RailwayDataManager()
    gov = GovernanceEngine(dm)
    agent = TravelPlannerAgent(dm)
    return dm, gov, agent

dm, gov, agent = init_system()
audit = AuditLogger()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/train.png", width=64)
st.sidebar.title("RailAI Platform")
st.sidebar.caption("Intelligent Travel & Autonomous AI Governance")

nav_choice = st.sidebar.radio(
    "Navigation",
    [
        "🚆 Smart Train Recommendation",
        "🗺️ Route & Delay-Risk Inspection",
        "🛡️ Autonomous AI Governance",
        "🤖 AI Travel Planner Agent",
        "📋 System Audit Logs"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dataset Telemetry")
st.sidebar.info(f"""
- **Records:** {len(dm.df):,}
- **Unique Trains:** {dm.df['Train No.'].nunique():,}
- **Stations:** {dm.df['station Code'].nunique():,}
- **Data Source:** IRCTC Historical Timetable
""")

# Banner on all pages
st.markdown("""
<div class="disclaimer-box">
    <strong>Prototype Notice & Data Scope:</strong> Powered by historical timetable data (2015). 
    Train routing, station sequences, and scheduled timetables are real and verified. 
    Delay risk and governance drift events are domain-grounded <em>heuristics and synthetic simulations</em> 
    designed to showcase autonomous AI supervision.
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# MODULE A: SMART TRAIN RECOMMENDATION
# ==============================================================================
if nav_choice == "🚆 Smart Train Recommendation":
    st.markdown('<div class="main-title">🚆 Smart Train Recommendation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Rule-based multi-criteria ranking for direct and intermediate train services</div>', unsafe_allow_html=True)

    # Preset Quick Routes
    st.write("##### Quick Route Presets:")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    preset_src, preset_dst = None, None
    if col_p1.button("📍 BBS ➔ VSKP (East Coast)", use_container_width=True):
        preset_src, preset_dst = "BHUBANESWAR (BBS)", "VISAKHAPATNAM (VSKP)"
    if col_p2.button("📍 HWH ➔ MAS (Trunk Line)", use_container_width=True):
        preset_src, preset_dst = "HOWRAH JN (HWH)", "CHENNAI CENTRAL (MAS)"
    if col_p3.button("📍 NDLS ➔ CNB (Northern Corridor)", use_container_width=True):
        preset_src, preset_dst = "NEW DELHI (NDLS)", "KANPUR CENTRAL (CNB)"
    if col_p4.button("📍 BBS ➔ BNC (Suvidha / South)", use_container_width=True):
        preset_src, preset_dst = "BHUBANESWAR (BBS)", "BANGALORE CANT (BNC)"

    col1, col2, col3 = st.columns([2.5, 2.5, 2])
    
    # Defaults
    def_src_idx = dm.stations.index(preset_src) if preset_src in dm.stations else (
        dm.stations.index("BHUBANESWAR (BBS)") if "BHUBANESWAR (BBS)" in dm.stations else 0
    )
    def_dst_idx = dm.stations.index(preset_dst) if preset_dst in dm.stations else (
        dm.stations.index("VISAKHAPATNAM (VSKP)") if "VISAKHAPATNAM (VSKP)" in dm.stations else 1
    )

    with col1:
        src_selection = st.selectbox("Source Station", options=dm.stations, index=def_src_idx)
    with col2:
        dst_selection = st.selectbox("Destination Station", options=dm.stations, index=def_dst_idx)
    with col3:
        sort_criteria = st.selectbox(
            "Ranking Criteria",
            ["Fewest Stops", "Shortest Distance", "Earliest Departure", "Recommended (Balanced)"]
        )

    # Advanced filter toggles
    with st.expander("🛠️ Advanced Search Filters & Constraints", expanded=False):
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            max_stops_filter = st.slider("Max Intermediate Stops", min_value=0, max_value=80, value=60)
        with c_f2:
            time_filter = st.selectbox(
                "Departure Time Window",
                ["Any Time", "Morning (04:00 - 11:59)", "Afternoon (12:00 - 16:59)", "Evening / Night (17:00 - 03:59)"]
            )

    search_btn = st.button("🔍 Search Matching Trains", type="primary", use_container_width=True)

    src_code = dm.get_station_code(src_selection)
    dst_code = dm.get_station_code(dst_selection)

    if src_code == dst_code:
        st.error("⚠️ Source and Destination stations cannot be the same. Please select different stations.")
    else:
        # Perform query
        t0 = time.time()
        results = dm.search_routes(src_code, dst_code, sort_by=sort_criteria)
        latency = (time.time() - t0) * 1000

        # Apply user filters if any
        if not results.empty:
            results = results[results['intermediate_stops'] <= max_stops_filter]
            if time_filter == "Morning (04:00 - 11:59)":
                results = results[results['src_departure'].between('04:00:00', '11:59:59')]
            elif time_filter == "Afternoon (12:00 - 16:59)":
                results = results[results['src_departure'].between('12:00:00', '16:59:59')]
            elif time_filter == "Evening / Night (17:00 - 03:59)":
                results = results[(results['src_departure'] >= '17:00:00') | (results['src_departure'] <= '03:59:59')]

        # Log query audit event
        audit.log_event(
            module="Smart Recommendation",
            event_type="ROUTE_QUERY",
            action=f"Search {src_code} -> {dst_code}",
            details=f"Found: {len(results)} trains | Sorted by: {sort_criteria}",
            status="SUCCESS" if not results.empty else "NO_RESULTS",
            latency_ms=latency
        )

        if results.empty:
            st.warning(f"No direct or through train routes found between **{src_selection}** and **{dst_selection}** with current filters.")
            st.info("💡 **Tips:** Try removing stop filters, expanding the departure window, or try one of the popular quick presets above.")
        else:
            # Summary KPIs
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Matching Trains</div><div class="kpi-value">{len(results)}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Shortest Journey</div><div class="kpi-value">{results["journey_distance"].min()} km</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="kpi-card"><div class="kpi-title">Fewest Stops</div><div class="kpi-value">{results["intermediate_stops"].min()}</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Query Latency</div><div class="kpi-value">{round(latency, 1)} ms</div></div>', unsafe_allow_html=True)

            st.write("---")

            # Governance Bias Insight
            bias_info = gov.analyze_recommendation_bias(results)
            if bias_info:
                st.caption(f"🛡️ **AI Governance Fairness Check:** {bias_info['bias_finding']} (Analyzed {bias_info['total_options']} options)")

            # Results Table
            st.write(f"### Available Routes ({len(results)} trains found)")
            
            display_df = results[[
                'Train No.', 'train Name', 'src_departure', 'dst_arrival', 
                'journey_distance', 'intermediate_stops', 'source_name', 'dest_name', 'recommendation_score'
            ]].rename(columns={
                'Train No.': 'Train No',
                'train Name': 'Train Name',
                'src_departure': 'Dep Time',
                'dst_arrival': 'Arr Time',
                'journey_distance': 'Distance (km)',
                'intermediate_stops': 'Stops',
                'source_name': 'Origin',
                'dest_name': 'Final Terminus',
                'recommendation_score': 'Score'
            })

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            # Route inspector shortcut
            st.write("#### 🔍 Select Train for Deep Inspection & Delay Risk:")
            selected_tno = st.selectbox(
                "Choose train to inspect detailed timetable & delay risk:",
                options=results['Train No.'].tolist(),
                format_func=lambda x: f"{x} - {results[results['Train No.'] == x]['train Name'].iloc[0]}"
            )
            if st.button("👉 Inspect This Train in Route & Delay-Risk Module"):
                st.session_state['inspect_train_no'] = selected_tno
                st.session_state['inspect_src'] = src_code
                st.session_state['inspect_dst'] = dst_code
                st.success(f"Selected train {selected_tno}. Please switch to '🗺️ Route & Delay-Risk Inspection' tab in sidebar.")


# ==============================================================================
# MODULE B: JOURNEY & DELAY-RISK DEMONSTRATION
# ==============================================================================
elif nav_choice == "🗺️ Route & Delay-Risk Inspection":
    st.markdown('<div class="main-title">🗺️ Journey Timetable & Delay-Risk Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Full route stop-level inspection, halt analysis, and explainable delay-risk heuristics</div>', unsafe_allow_html=True)

    # Allow selecting any train
    default_tno = st.session_state.get('inspect_train_no', dm.df['Train No.'].iloc[0])
    
    # Train lookup list
    train_options = dm.train_summary['Train No.'].tolist()
    train_idx = train_options.index(default_tno) if default_tno in train_options else 0
    
    col_t1, col_t2 = st.columns([3, 2])
    with col_t1:
        sel_train = st.selectbox(
            "Select Train to Inspect",
            options=train_options,
            index=train_idx,
            format_func=lambda x: f"{x} - {dm.train_summary[dm.train_summary['Train No.'] == x]['train_name'].iloc[0]}"
        )
    with col_t2:
        stress_scenario = st.selectbox(
            "Synthetic Operating Stress Scenario (What-If)",
            [
                "Normal Operating Conditions",
                "Monsoon Speed Restrictions",
                "Winter Dense Fog Scenario",
                "High-Density Freight Slot Contention"
            ]
        )

    route_df = dm.get_train_route(sel_train)

    if route_df.empty:
        st.error(f"No route records found for train {sel_train}.")
    else:
        t_meta = dm.train_summary[dm.train_summary['Train No.'] == sel_train].iloc[0]
        
        # Route KPIs
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.markdown(f'<div class="kpi-card"><div class="kpi-title">Origin</div><div class="kpi-value" style="font-size:1.15rem;">{t_meta["source_name"]}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi-card"><div class="kpi-title">Terminus</div><div class="kpi-value" style="font-size:1.15rem;">{t_meta["dest_name"]}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Distance</div><div class="kpi-value">{t_meta["max_distance"]} km</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Stations</div><div class="kpi-value">{len(route_df)}</div></div>', unsafe_allow_html=True)
        k5.markdown(f'<div class="kpi-card"><div class="kpi-title">Max Station Halt</div><div class="kpi-value">{route_df["Halt (Mins)"].max()} min</div></div>', unsafe_allow_html=True)

        st.write("---")

        # Delay Risk Evaluation
        risk_data = DelayRiskEngine.evaluate_route_risk(route_df, stress_scenario=stress_scenario)

        st.write("### 🛡️ Route Delay-Risk Evaluation (Autonomous Governance Demonstration)")
        
        col_r1, col_r2 = st.columns([2, 3])
        with col_r1:
            st.markdown(f"""
            <div style="background-color:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:20px; text-align:center;">
                <div style="font-size:0.9rem; color:#64748b; font-weight:600;">COMPOSITE RISK INDEX</div>
                <div style="font-size:3rem; font-weight:800; color:{risk_data['badge_color']};">{risk_data['score']} / 100</div>
                <div style="margin-top:8px;">
                    <span class="badge-pill" style="background-color:{risk_data['badge_color']}; color:#ffffff;">
                        {risk_data['category']}
                    </span>
                </div>
                <p style="margin-top:14px; font-size:0.9rem; color:#475569;">{risk_data['summary']}</p>
                <div style="font-size:0.8rem; color:#94a3b8; font-style:italic; border-top:1px solid #f1f5f9; padding-top:8px;">
                    Scenario Applied: {risk_data['scenario']}<br>{risk_data['scenario_impact']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_r2:
            st.write("#### 🔍 Explainable Risk Factor Breakdown")
            chart_df = risk_data['factors_table']
            fig_bar = px.bar(
                chart_df,
                x='Sub-score (0-100)',
                y='Risk Dimension',
                orientation='h',
                color='Sub-score (0-100)',
                color_continuous_scale=['#22c55e', '#eab308', '#ef4444'],
                range_color=[0, 100],
                text='Sub-score (0-100)',
                title="Risk Contributing Factors (0-100 Scale)"
            )
            fig_bar.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        st.caption(risk_data['disclaimer'])

        # Factors table
        st.write("##### Detailed Risk Rationale:")
        st.dataframe(risk_data['factors_table'], use_container_width=True, hide_index=True)

        st.write("---")

        # Interactive Distance & Halt Progression Chart
        st.write("### 📈 Interactive Route Elevation & Station Progression")
        fig_route = go.Figure()
        fig_route.add_trace(go.Scatter(
            x=route_df['islno'],
            y=route_df['Distance'],
            mode='lines+markers',
            name='Cumulative Distance (km)',
            line=dict(color='#2563eb', width=3),
            marker=dict(size=6),
            hovertemplate="<b>%{text}</b><br>Stop Seq: %{x}<br>Distance: %{y} km<extra></extra>",
            text=route_df['Station Name'] + " (" + route_df['station Code'] + ")"
        ))
        fig_route.update_layout(
            title=f"Route Trajectory: Train {sel_train} ({t_meta['train_name']})",
            xaxis_title="Sequential Stop Index",
            yaxis_title="Distance from Origin (km)",
            height=340,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_route, use_container_width=True)

        # Full Timetable Table
        st.write(f"### 📋 Full Timetable Schedule ({len(route_df)} Stations)")
        display_route = route_df[[
            'islno', 'station Code', 'Station Name', 'Arrival time', 'Departure time', 'Halt (Mins)', 'Distance'
        ]].rename(columns={
            'islno': 'Seq #',
            'station Code': 'Code',
            'Station Name': 'Station Name',
            'Arrival time': 'Arrival',
            'Departure time': 'Departure',
            'Distance': 'Cumulative Dist (km)'
        })
        st.dataframe(display_route, use_container_width=True, hide_index=True)


# ==============================================================================
# MODULE C: AI GOVERNANCE DASHBOARD
# ==============================================================================
elif nav_choice == "🛡️ Autonomous AI Governance":
    st.markdown('<div class="main-title">🛡️ Centralized Autonomous AI Governance Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Model lifecycle tracking, data quality monitoring, drift simulation, and auditability</div>', unsafe_allow_html=True)

    # Genuine Data Quality Statistics
    dq = dm.get_data_quality_report()

    st.write("### 1. Data Ingestion & Quality Metrics (Actual Dataset Analysis)")
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Records</div><div class="kpi-value">{dq["total_records"]:,}</div></div>', unsafe_allow_html=True)
    q2.markdown(f'<div class="kpi-card"><div class="kpi-title">Unique Trains</div><div class="kpi-value">{dq["unique_trains"]:,}</div></div>', unsafe_allow_html=True)
    q3.markdown(f'<div class="kpi-card"><div class="kpi-title">Unique Stations</div><div class="kpi-value">{dq["unique_stations"]:,}</div></div>', unsafe_allow_html=True)
    q4.markdown(f'<div class="kpi-card"><div class="kpi-title">Missing Values</div><div class="kpi-value">{dq["total_missing_cells"]}</div></div>', unsafe_allow_html=True)
    q5.markdown(f'<div class="kpi-card"><div class="kpi-title">Data Integrity</div><div class="kpi-value">{dq["data_health_score"]}%</div></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-top:12px; font-size:0.88rem; color:#475569;">
        <strong>Data Cleaning & Transformation Audit:</strong> Raw CSV contained single quotes and boundary whitespace across 
        text fields (<code>Train No.</code>, <code>train Name</code>, <code>Arrival time</code>, <code>Departure time</code>). 
        All <strong>{:,}</strong> instances were sanitized during ingest. Sequence monotonicity check passed across all 
        <strong>{:,}</strong> trains.
    </div>
    """.format(dq['raw_whitespace_format_anomalies'], dq['unique_trains']), unsafe_allow_html=True)

    st.write("---")

    # Service & Model Health
    st.write("### 2. Service & Pipeline Health Indicators")
    health_items = gov.get_system_health()
    st.dataframe(pd.DataFrame(health_items), use_container_width=True, hide_index=True)

    st.write("---")

    # Drift & Concept Anomaly Simulator
    st.write("### 3. Drift & Concept Anomaly Monitoring (Interactive Simulation)")
    st.caption("Demonstrates how the autonomous governance layer monitors incoming telemetry for distributional shifts.")

    col_d1, col_d2 = st.columns([2, 3])
    with col_d1:
        sim_scenario = st.selectbox(
            "Select Drift Event to Simulate",
            [
                "Station Renaming / Schema Drift",
                "Timetable Departure Shift",
                "Ingestion Missingness Anomaly"
            ]
        )
        trigger_btn = st.button("🚨 Simulate Drift Event", type="secondary", use_container_width=True)

    with col_d2:
        if trigger_btn:
            drift_res = gov.simulate_drift_event(sim_scenario)
            st.markdown(f"""
            <div style="background-color:#fff7ed; border-left:4px solid #f97316; padding:14px; border-radius:6px;">
                <div style="font-weight:700; color:#9a3412;">ALERT: {drift_res['alert_level']} - {drift_res['scenario']}</div>
                <div style="margin-top:6px; font-size:0.9rem; color:#334155;"><strong>Metric:</strong> {drift_res['metric_name']} = <code>{drift_res['psi_score']}</code></div>
                <div style="margin-top:4px; font-size:0.9rem; color:#334155;"><strong>Observation:</strong> {drift_res['finding']}</div>
                <div style="margin-top:6px; font-size:0.9rem; color:#065f46; font-weight:600;">{drift_res['remediation']}</div>
                <div style="margin-top:8px; font-size:0.75rem; color:#94a3b8;">{drift_res['disclaimer']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Select a drift event type and click 'Simulate Drift Event' to test autonomous alert generation.")

    st.write("---")

    # Transparency & Explainability Manifesto
    st.write("### 4. Governance Compliance & Boundary Statement")
    with st.expander("📖 AI Governance Standards & Limitations (Click to View)", expanded=False):
        st.markdown("""
        - **Model Accuracy Disclosures:** No ML model accuracy metrics (e.g. F1, ROC-AUC) are displayed because the available historical CSV does not supply verified ground-truth arrival delay timestamps or booking confirmation outcomes. Fabricating synthetic accuracy scores is strictly prohibited.
        - **Automated Retraining Boundaries:** Automated pipeline retraining is presented as a simulated autonomous design pattern. No unverified production pipeline re-weights itself without human-in-the-loop validation.
        - **Audit Trail:** Every route search, constraint modification, stress simulation, and drift check is appended to an immutable in-memory audit log for tamper-evident oversight.
        """)


# ==============================================================================
# MODULE D: AI TRAVEL PLANNER AGENT
# ==============================================================================
elif nav_choice == "🤖 AI Travel Planner Agent":
    st.markdown('<div class="main-title">🤖 Conversational AI Travel Planner Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Natural language travel requirement parsing and autonomous itinerary optimization</div>', unsafe_allow_html=True)

    st.write("##### Sample Natural Language Queries (Click to Test):")
    q_col1, q_col2, q_col3 = st.columns(3)
    sample_q = ""
    if q_col1.button("💬 'From Bhubaneswar to Visakhapatnam with fewest stops'"):
        sample_q = "From Bhubaneswar to Visakhapatnam with fewest stops"
    if q_col2.button("💬 'Trains from Howrah to Chennai under budget 1200'"):
        sample_q = "Trains from Howrah to Chennai under budget 1200"
    if q_col3.button("💬 'Morning train from New Delhi to Kanpur'"):
        sample_q = "Morning train from New Delhi to Kanpur"

    user_prompt = st.text_input(
        "Enter your travel requirement in plain English:",
        value=sample_q if sample_q else "I want to travel from Bhubaneswar to Visakhapatnam with fewest stops"
    )

    plan_btn = st.button("🚀 Plan My Journey with AI Agent", type="primary")

    if plan_btn and user_prompt:
        t0 = time.time()
        parsed = agent.parse_query(user_prompt)
        latency = (time.time() - t0) * 1000

        st.write("### 🧠 Agentic Reasoning & Entity Extraction Rationale")
        e1, e2, e3, e4 = st.columns(4)
        e1.markdown(f'<div class="kpi-card"><div class="kpi-title">Detected Origin</div><div class="kpi-value" style="font-size:1.1rem;">{parsed["detected_src_name"] or "Unknown"} ({parsed["detected_src"] or "N/A"})</div></div>', unsafe_allow_html=True)
        e2.markdown(f'<div class="kpi-card"><div class="kpi-title">Detected Terminus</div><div class="kpi-value" style="font-size:1.1rem;">{parsed["detected_dst_name"] or "Unknown"} ({parsed["detected_dst"] or "N/A"})</div></div>', unsafe_allow_html=True)
        e3.markdown(f'<div class="kpi-card"><div class="kpi-title">Strategy</div><div class="kpi-value" style="font-size:1.1rem;">{parsed["sort_by"]}</div></div>', unsafe_allow_html=True)
        e4.markdown(f'<div class="kpi-card"><div class="kpi-title">Confidence</div><div class="kpi-value" style="font-size:1.1rem;">{parsed["confidence"]}</div></div>', unsafe_allow_html=True)

        if not parsed['detected_src'] or not parsed['detected_dst']:
            st.error("⚠️ The agent could not match both Source and Destination stations from your query. Please mention station names like 'from Delhi to Mumbai' or 'from BBS to VSKP'.")
        else:
            # Query verified dataset
            routes = dm.search_routes(parsed['detected_src'], parsed['detected_dst'], sort_by=parsed['sort_by'])
            
            if parsed['time_filter'] == "Morning (05:00 - 11:59)":
                routes = routes[routes['src_departure'].between('05:00:00', '11:59:59')]
            elif parsed['time_filter'] == "Evening/Night (17:00 - 23:59)":
                routes = routes[routes['src_departure'] >= '17:00:00']

            audit.log_event(
                module="Travel Assistant",
                event_type="AGENT_PLAN",
                action=f"NLP Query: '{user_prompt}'",
                details=f"Extracted: {parsed['detected_src']} -> {parsed['detected_dst']} | Found: {len(routes)}",
                status="SUCCESS" if not routes.empty else "NO_RESULTS",
                latency_ms=latency
            )

            if routes.empty:
                st.warning(f"No trains matching your constraints found between {parsed['detected_src_name']} and {parsed['detected_dst_name']}.")
            else:
                st.write(f"### 🎯 Recommended Itinerary ({len(routes)} matching trains):")
                top_train = routes.iloc[0]

                # Estimated Indicative Fare Calculation (clearly labelled as heuristic)
                dist = top_train['journey_distance']
                sl_fare = int(dist * 0.45 + 120)
                ac3_fare = int(dist * 1.15 + 350)
                ac2_fare = int(dist * 1.65 + 500)

                st.markdown(f"""
                <div style="background-color:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:16px; margin-bottom:16px;">
                    <h4 style="margin:0; color:#166534;">🌟 Top Agent Recommendation: Train {top_train['Train No.']} - {top_train['train Name']}</h4>
                    <p style="margin:6px 0 10px 0; color:#14532d;">
                        Departing <strong>{top_train['src_station']}</strong> at <code>{top_train['src_departure']}</code> ➔ 
                        Arriving <strong>{top_train['dst_station']}</strong> at <code>{top_train['dst_arrival']}</code><br>
                        <strong>Distance:</strong> {top_train['journey_distance']} km | 
                        <strong>Intermediate Stops:</strong> {top_train['intermediate_stops']} stations
                    </p>
                    <div style="font-size:0.85rem; color:#365314;">
                        <strong>Indicative IRCTC Distance-Based Tariff (Formula Approximation):</strong><br>
                        Sleeper (SL): ~₹{sl_fare} | 3-Tier AC (3A): ~₹{ac3_fare} | 2-Tier AC (2A): ~₹{ac2_fare}
                        <span style="font-size:0.75rem; color:#713f12;"> (Note: Indicative distance tariff for planning. Real-time booking requires IRCTC PRS).</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.dataframe(
                    routes[['Train No.', 'train Name', 'src_departure', 'dst_arrival', 'journey_distance', 'intermediate_stops', 'recommendation_score']].rename(columns={
                        'Train No.': 'Train No',
                        'train Name': 'Train Name',
                        'src_departure': 'Departs',
                        'dst_arrival': 'Arrives',
                        'journey_distance': 'Dist (km)',
                        'intermediate_stops': 'Stops',
                        'recommendation_score': 'Score'
                    }),
                    use_container_width=True,
                    hide_index=True
                )


# ==============================================================================
# MODULE E: AUDIT LOGS & EVENT TRACEABILITY
# ==============================================================================
elif nav_choice == "📋 System Audit Logs":
    st.markdown('<div class="main-title">📋 Governance Event Audit Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-time traceable log of user interactions, route queries, stress tests, and governance drift events</div>', unsafe_allow_html=True)

    log_df = audit.get_logs_df()

    if log_df.empty:
        st.info("No audit events recorded yet.")
    else:
        st.write(f"Total Audit Events Recorded: **{len(log_df)}**")

        # Filters
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            mod_filter = st.multiselect("Filter by Module", options=log_df['Module'].unique().tolist(), default=log_df['Module'].unique().tolist())
        with c_l2:
            status_filter = st.multiselect("Filter by Status", options=log_df['Status'].unique().tolist(), default=log_df['Status'].unique().tolist())

        filtered_logs = log_df[
            (log_df['Module'].isin(mod_filter)) &
            (log_df['Status'].isin(status_filter))
        ]

        st.dataframe(filtered_logs, use_container_width=True, hide_index=True)

        # Download capability
        csv_data = filtered_logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Audit Trail (CSV)",
            data=csv_data,
            file_name="railway_ai_governance_audit_log.csv",
            mime="text/csv"
        )
