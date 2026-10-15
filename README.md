# AI-Powered Intelligent Railway Travel & Autonomous AI Governance Platform

A high-performance MVP built with **Python**, **Streamlit**, **Pandas**, and **Plotly** on historical Indian Railways timetable and station data.

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📦 Project Architecture & Files

| File | Purpose |
| :--- | :--- |
| [`app.py`](file:///c:/train/app.py) | Main interactive multi-module Streamlit dashboard with custom CSS, KPI cards, and Plotly visualizations. |
| [`data_manager.py`](file:///c:/train/data_manager.py) | Caches, cleans whitespace/quotes, and executes high-speed route searches and sequence monotonicity checks across 69,006 records. |
| [`risk_engine.py`](file:///c:/train/risk_engine.py) | Domain-grounded explainable delay-risk heuristic and synthetic stress test simulator (What-If weather/congestion scenarios). |
| [`governance_engine.py`](file:///c:/train/governance_engine.py) | Centralized AI governance layer, real-time SLA telemetry, recommendation bias audit, and simulated drift event generators. |
| [`travel_assistant.py`](file:///c:/train/travel_assistant.py) | Natural language query intent and entity parser for autonomous conversational travel planning. |
| [`requirements.txt`](file:///c:/train/requirements.txt) | Python dependencies (`streamlit`, `pandas`, `plotly`, `scikit-learn`). |
| [`isl_wise_train_detail_03082015_v1.csv`](file:///c:/train/isl_wise_train_detail_03082015_v1.csv) | Historical timetable dataset (69,006 stop records, 2,810 trains, 4,344 stations). |

---

## 🛠️ Implemented Modules

### 1. Module A: Smart Train Recommendation Engine
- **Searchable Stations:** Fuzzy lookup across 4,344 stations with popular one-click presets (e.g. BBS ➔ VSKP, HWH ➔ MAS, NDLS ➔ CNB).
- **Sequential Route Matching:** Matches direct and intermediate through-trains with valid sequence ordering (`islno_src < islno_dst`).
- **Dynamic Metrics:** Computes journey distance (`dist_dst - dist_src`) and exact count of intermediate stops.
- **Multi-Criteria Ranking:**
  - ⚡ Fewest Intermediate Stops
  - 📏 Shortest Distance
  - 🌅 Earliest Departure
  - 🌟 Recommended Balanced Composite Score
- **Input Validation & Anomaly Protection:** Handles source == destination, empty searches, and departure time windows.

### 2. Module B: Journey Route & Delay-Risk Assessment
- **Full Route Timetable:** Complete stop schedule with arrival, departure, cumulative distance, and calculated station dwell/halt durations.
- **Route Elevation Plot:** Interactive Plotly chart tracing route progression from origin to terminus.
- **Explainable Delay-Risk Heuristic:**
  - *Strictly labelled as an illustrative heuristic/synthetic demonstration* (as historical 2015 data does not contain real-time delay logs).
  - Risk factors: Corridor Distance (30%), Intermediate Stop Density (25%), Congested Bottleneck Junction Exposure (25%), Halt Outliers (10%), Midnight Freight Transit (10%).
- **Interactive Stress Simulator:** Test what-if operating scenarios (Monsoon Speed Restrictions, Winter Fog, High-Density Freight Contention).

### 3. Module C: Autonomous AI Governance Dashboard
- **Data Quality & Integrity KPI Cards:** Live statistics calculated from loaded CSV (69,006 records, 2,810 trains, 0 missing cells, 200k+ string artifacts cleaned, 96.5% Data Health Index).
- **Service SLA & Component Telemetry:** Real-time health monitoring of route engines, data sanitizers, and NLP agents.
- **Fairness & Bias Detection:** Analyzes recommendation distributions (Suvidha/Premium vs Express/Mail) to prevent platform bias.
- **Simulated Drift & Anomaly Generator:** Interactive simulation of Station Renaming / Schema Drift, Timetable Shifts, and Ingestion Missingness with autonomous remediation recommendations.

### 4. Module D: Conversational AI Travel Planner Agent
- Understands natural language travel requests (e.g., *"From Bhubaneswar to Visakhapatnam with fewest stops"* or *"Morning train from New Delhi to Kanpur"*).
- Extracts entities, applies ranking constraints, queries verified routes, and calculates indicative distance-based tariff breakdowns.

### 5. Module E: System Audit Trail & Event Logs
- In-memory event logger recording all searches, filters, stress simulations, and governance alerts with timestamps and latency tracking.
- CSV export for regulatory auditability and compliance.

---

## ⚖️ Data Scope & Limitations
- **No Real-Time Delays:** The dataset provides scheduled historical timetables (2015). Delay risks are domain heuristics and not validated ML models.
- **No PNR / Booking Outcomes:** Ground truth booking outcomes or dynamic fare matrices are not present in this dataset; distance-based tariffs are provided as approximations for journey planning.
