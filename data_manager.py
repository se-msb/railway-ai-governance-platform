"""
data_manager.py - High-performance data processing and train route queries.
"""
import pandas as pd
import numpy as np
from datetime import datetime

DATA_PATH = 'isl_wise_train_detail_03082015_v1.csv'

class RailwayDataManager:
    def __init__(self, csv_path=DATA_PATH):
        self.csv_path = csv_path
        self.df = None
        self.stations = []
        self.station_map = {}
        self.train_summary = None
        self.load_and_clean_data()

    def load_and_clean_data(self):
        df = pd.read_csv(self.csv_path, low_memory=False)
        
        # Strip string columns of whitespace and single/double quotes
        str_cols = df.select_dtypes(include='object').columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip().str.strip("'\"")
            
        # Ensure correct numerical types
        df['islno'] = pd.to_numeric(df['islno'], errors='coerce').fillna(0).astype(int)
        df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce').fillna(0).astype(int)
        
        # Create full station label: "STATION NAME (CODE)"
        df['Station_Label'] = df['Station Name'] + " (" + df['station Code'] + ")"
        
        self.df = df
        
        # Unique stations sorted
        station_df = df[['station Code', 'Station Name', 'Station_Label']].drop_duplicates()
        station_df = station_df.sort_values('Station Name')
        self.stations = station_df['Station_Label'].tolist()
        self.station_map = dict(zip(station_df['Station_Label'], station_df['station Code']))
        self.code_to_name = dict(zip(station_df['station Code'], station_df['Station Name']))

        # Cache train-level metadata
        self.train_summary = df.groupby('Train No.').agg(
            train_name=('train Name', 'first'),
            source_code=('Source Station Code', 'first'),
            source_name=('source Station Name', 'first'),
            dest_code=('Destination station Code', 'first'),
            dest_name=('Destination Station Name', 'first'),
            total_stops=('islno', 'max'),
            max_distance=('Distance', 'max')
        ).reset_index()

    def get_station_code(self, label_or_code):
        if not label_or_code:
            return None
        label_or_code = label_or_code.strip()
        if label_or_code in self.station_map:
            return self.station_map[label_or_code]
        # Match by direct code
        code_upper = label_or_code.upper()
        if code_upper in self.code_to_name:
            return code_upper
        return None

    def search_routes(self, src_code, dst_code, sort_by='Fewest Stops'):
        """
        Search trains passing through both src_code and dst_code in sequential order.
        """
        if not src_code or not dst_code:
            return pd.DataFrame()
            
        src_df = self.df[self.df['station Code'] == src_code][
            ['Train No.', 'train Name', 'islno', 'Departure time', 'Distance', 'Station Name']
        ].rename(columns={
            'islno': 'src_islno',
            'Departure time': 'src_departure',
            'Distance': 'src_dist',
            'Station Name': 'src_station'
        })
        
        dst_df = self.df[self.df['station Code'] == dst_code][
            ['Train No.', 'islno', 'Arrival time', 'Distance', 'Station Name']
        ].rename(columns={
            'islno': 'dst_islno',
            'Arrival time': 'dst_arrival',
            'Distance': 'dst_dist',
            'Station Name': 'dst_station'
        })
        
        merged = pd.merge(src_df, dst_df, on='Train No.')
        valid = merged[merged['src_islno'] < merged['dst_islno']].copy()
        
        if valid.empty:
            return pd.DataFrame()
            
        valid['journey_distance'] = valid['dst_dist'] - valid['src_dist']
        valid['intermediate_stops'] = valid['dst_islno'] - valid['src_islno'] - 1
        
        # Merge overall train origin and destination
        valid = valid.merge(
            self.train_summary[['Train No.', 'source_code', 'source_name', 'dest_code', 'dest_name', 'total_stops']],
            on='Train No.',
            how='left'
        )

        # Transparent rule-based composite ranking score (lower is better)
        # Weights: Stops count (1x) + Distance/50 (1x)
        valid['recommendation_score'] = (
            valid['intermediate_stops'] * 1.5 + 
            (valid['journey_distance'] / 50.0)
        ).round(1)

        # Sorting logic
        if sort_by == 'Fewest Stops':
            valid = valid.sort_values(['intermediate_stops', 'journey_distance'])
        elif sort_by == 'Shortest Distance':
            valid = valid.sort_values(['journey_distance', 'intermediate_stops'])
        elif sort_by == 'Earliest Departure':
            valid = valid.sort_values('src_departure')
        elif sort_by == 'Recommended (Balanced)':
            valid = valid.sort_values('recommendation_score')
            
        return valid

    def get_train_route(self, train_no):
        """
        Get all intermediate stations and schedule for a specific train.
        """
        route = self.df[self.df['Train No.'] == str(train_no)].sort_values('islno').copy()
        if route.empty:
            return pd.DataFrame()
            
        # Calculate halt duration in minutes if arrival and departure are both valid times
        def calc_halt(row):
            arr = row['Arrival time']
            dep = row['Departure time']
            if arr == '00:00:00' or dep == '00:00:00':
                return 0
            try:
                t1 = datetime.strptime(arr, '%H:%M:%S')
                t2 = datetime.strptime(dep, '%H:%M:%S')
                diff = (t2 - t1).total_seconds() / 60
                return int(diff) if diff >= 0 else int(diff + 1440)
            except Exception:
                return 0

        route['Halt (Mins)'] = route.apply(calc_halt, axis=1)
        return route

    def get_data_quality_report(self):
        """
        Generates genuine data quality and integrity statistics from loaded dataset.
        """
        raw_df = pd.read_csv(self.csv_path, low_memory=False)
        total_rows = len(raw_df)
        
        # Count formatting discrepancies in raw data
        raw_whitespace_issues = 0
        for col in raw_df.select_dtypes(include='object').columns:
            has_ws = raw_df[col].astype(str).str.contains(r"^\s|\s$|'|\"", regex=True).sum()
            raw_whitespace_issues += has_ws
            
        null_counts = raw_df.isnull().sum().to_dict()
        
        # Check monotonic islno sequencing per train
        non_monotonic_trains = 0
        for t_no, group in self.df.groupby('Train No.'):
            islnos = group['islno'].tolist()
            if islnos != sorted(islnos):
                non_monotonic_trains += 1
                
        # Station code discrepancies
        unique_codes = self.df['station Code'].nunique()
        unique_names = self.df['Station Name'].nunique()

        return {
            "total_records": total_rows,
            "unique_trains": self.df['Train No.'].nunique(),
            "unique_stations": unique_codes,
            "unique_station_names": unique_names,
            "raw_whitespace_format_anomalies": int(raw_whitespace_issues),
            "missing_values_raw": null_counts,
            "total_missing_cells": int(raw_df.isnull().sum().sum()),
            "non_monotonic_sequences": non_monotonic_trains,
            "data_health_score": round(100.0 - (raw_whitespace_issues / (total_rows * len(raw_df.columns)) * 5.0), 2)
        }
