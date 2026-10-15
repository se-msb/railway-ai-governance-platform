"""
risk_engine.py - Explainable Delay Risk Heuristic & Synthetic Stress Simulator
NOTE: Strictly labelled as an illustrative heuristic/synthetic demonstration as actual
historical delay timestamps are not present in the 2015 timetable dataset.
"""
import pandas as pd
import numpy as np

# Known high-congestion railway junctions in Indian Railways network
CONGESTED_JUNCTIONS = {
    'NDLS', 'DLI', 'NZM',  # Delhi cluster
    'CNB', 'ALD', 'MGS', 'DDU',  # Prayagraj/Kanpur/Deen Dayal Upadhyaya freight-dense corridor
    'BZA', 'BNC', 'SBC',   # South Central / Southern hubs
    'HWH', 'SDAH',         # Kolkata cluster
    'BCT', 'CSTM', 'BDTS', # Mumbai cluster
    'BPL', 'ET', 'NGP',    # Central transit trunk junctions
    'GKP', 'PNBE', 'GHY'   # Northern/Eastern transit points
}

class DelayRiskEngine:
    @staticmethod
    def evaluate_route_risk(route_df, stress_scenario="Normal Operating Conditions"):
        """
        Calculates domain-grounded explainable delay risk heuristic.
        Returns:
            dict containing risk score, category, factors breakdown, and explainability notes.
        """
        if route_df.empty:
            return None
            
        total_dist = route_df['Distance'].max() - route_df['Distance'].min()
        total_stops = len(route_df)
        station_codes = set(route_df['station Code'].str.strip().str.upper())
        
        # 1. Congested Junctions crossed
        congested_intersections = station_codes.intersection(CONGESTED_JUNCTIONS)
        num_congested = len(congested_intersections)
        
        # 2. Halt distribution
        halts = route_df.get('Halt (Mins)', pd.Series([0]))
        max_halt = halts.max() if not halts.empty else 0
        total_halt_time = halts.sum() if not halts.empty else 0
        
        # 3. Overnight travel indicator (crosses 00:00 to 05:00)
        has_night_segment = False
        for dep in route_df['Departure time']:
            if dep and dep != '00:00:00':
                hour = int(dep.split(':')[0]) if ':' in dep else 0
                if 0 <= hour <= 5:
                    has_night_segment = True
                    break

        # Compute factor scores (0 - 100 scale components)
        # Factor A: Distance Risk (Weight: 30%)
        # > 1500 km -> 100%, 0 km -> 10%
        distance_factor = min(100.0, max(10.0, (total_dist / 1500.0) * 100.0))
        
        # Factor B: Stop Density & Dwell Risk (Weight: 25%)
        # > 35 stops -> 100%
        stop_factor = min(100.0, max(10.0, (total_stops / 35.0) * 100.0))
        
        # Factor C: High-Density Bottleneck Exposure (Weight: 25%)
        # 3+ congested junctions -> 100%
        junction_factor = min(100.0, (num_congested / 3.0) * 100.0)
        
        # Factor D: Operational Halts & Reversals (Weight: 10%)
        halt_factor = 90.0 if max_halt >= 20 else (50.0 if max_halt >= 10 else 20.0)
        
        # Factor E: Midnight Track Slot Contention (Weight: 10%)
        night_factor = 75.0 if has_night_segment else 20.0

        # Base composite score
        base_score = (
            distance_factor * 0.30 +
            stop_factor * 0.25 +
            junction_factor * 0.25 +
            halt_factor * 0.10 +
            night_factor * 0.10
        )

        # Apply synthetic scenario multipliers if selected
        scenario_multiplier = 1.0
        scenario_impact = "No extra synthetic stress applied."
        if stress_scenario == "Monsoon Speed Restrictions":
            scenario_multiplier = 1.25
            scenario_impact = "Added +25% delay penalty for wet tracks, cautionary signaling & slow zones."
        elif stress_scenario == "Winter Dense Fog Scenario":
            scenario_multiplier = 1.35
            scenario_impact = "Added +35% delay penalty due to restricted speed (60 km/h) & reduced visibility."
        elif stress_scenario == "High-Density Freight Slot Contention":
            scenario_multiplier = 1.20
            scenario_impact = "Added +20% delay penalty for loop-line siding waits & freight priority overtaking."

        final_score = min(100.0, round(base_score * scenario_multiplier, 1))

        # Categorize
        if final_score < 30:
            category = "Low Risk"
            badge_color = "#22c55e"
            summary_desc = "Short to medium route with minimal junction contention; high on-time reliability expected."
        elif final_score < 55:
            category = "Moderate Risk"
            badge_color = "#eab308"
            summary_desc = "Standard inter-city service; minor delay vulnerability during platform reassignments."
        elif final_score < 75:
            category = "Elevated Risk"
            badge_color = "#f97316"
            summary_desc = "Long corridor passing multiple high-density traffic nodes; buffer time recommended."
        else:
            category = "High Risk"
            badge_color = "#ef4444"
            summary_desc = "Trans-continental long-haul route crossing severe bottleneck junctions; high probability of cascading delays."

        factors_table = pd.DataFrame([
            {
                "Risk Dimension": "Corridor Distance",
                "Weight": "30%",
                "Observed Metric": f"{total_dist} km",
                "Sub-score (0-100)": round(distance_factor, 1),
                "Operational Context": "Distances > 1000km accumulate sectional cascading delays"
            },
            {
                "Risk Dimension": "Intermediate Stops & Dwell",
                "Weight": "25%",
                "Observed Metric": f"{total_stops} stations",
                "Sub-score (0-100)": round(stop_factor, 1),
                "Operational Context": "Each station adds passenger boarding variance & signal clearance wait"
            },
            {
                "Risk Dimension": "Congested Hub Exposure",
                "Weight": "25%",
                "Observed Metric": f"{num_congested} hubs ({', '.join(congested_intersections) if congested_intersections else 'None'})",
                "Sub-score (0-100)": round(junction_factor, 1),
                "Operational Context": "Passage through freight/passenger saturated junctions"
            },
            {
                "Risk Dimension": "Halt Duration Outliers",
                "Weight": "10%",
                "Observed Metric": f"Max: {max_halt} min | Total: {total_halt_time} min",
                "Sub-score (0-100)": round(halt_factor, 1),
                "Operational Context": "Halts ≥ 20 mins involve loco turnaround, catering or rake re-marshaling"
            },
            {
                "Risk Dimension": "Night Freight Transit",
                "Weight": "10%",
                "Observed Metric": "Active" if has_night_segment else "Inactive",
                "Sub-score (0-100)": round(night_factor, 1),
                "Operational Context": "00:00-05:00 hours encounter heavy freight rake crossing"
            }
        ])

        return {
            "score": final_score,
            "category": category,
            "badge_color": badge_color,
            "summary": summary_desc,
            "congested_hubs": list(congested_intersections),
            "factors_table": factors_table,
            "scenario": stress_scenario,
            "scenario_impact": scenario_impact,
            "disclaimer": (
                "⚠️ SYNTHETIC HEURISTIC DEMONSTRATION ONLY: The historical dataset (2015) provides "
                "published timetables without realized delay records. The score is computed using a rule-based "
                "operational risk model and should NOT be interpreted as a verified production ML prediction."
            )
        }
