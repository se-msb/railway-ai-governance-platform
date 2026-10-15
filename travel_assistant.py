"""
travel_assistant.py - Natural language query understanding for railway travel planning.
"""
import re
import pandas as pd

class TravelPlannerAgent:
    def __init__(self, data_manager):
        self.dm = data_manager
        # Build station keyword search index
        self.keywords_to_code = {}
        for label, code in self.dm.station_map.items():
            name = self.dm.code_to_name.get(code, "").lower()
            code_l = code.lower()
            self.keywords_to_code[code_l] = code
            self.keywords_to_code[name] = code
            # Also add individual significant words if length >= 4
            for token in name.split():
                if len(token) >= 4 and token not in {'cant', 'junction', 'jn', 'city', 'road', 'central', 'term'}:
                    if token not in self.keywords_to_code:
                        self.keywords_to_code[token] = code

    def parse_query(self, user_query):
        """
        Extracts source, destination, preferences, and constraints from natural language text.
        """
        text = user_query.lower()
        
        # 1. Look for patterns like "from <X> to <Y>"
        from_to_match = re.search(r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+(?:under|before|after|with|in|at|$)|$)', text)
        
        src_candidate = None
        dst_candidate = None
        
        if from_to_match:
            src_candidate = from_to_match.group(1).strip()
            dst_candidate = from_to_match.group(2).strip()
        else:
            # Try splitting by "to"
            to_match = re.search(r'([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+(?:under|before|after|with|in|at|$)|$)', text)
            if to_match:
                src_candidate = to_match.group(1).strip()
                dst_candidate = to_match.group(2).strip()

        # Resolve candidate strings to station codes
        src_code = self._resolve_station(src_candidate) if src_candidate else None
        dst_code = self._resolve_station(dst_candidate) if dst_candidate else None

        # Preferences
        sort_by = "Recommended (Balanced)"
        if "fewest stops" in text or "least stops" in text or "fastest" in text:
            sort_by = "Fewest Stops"
        elif "shortest" in text or "minimum distance" in text:
            sort_by = "Shortest Distance"
        elif "early" in text or "morning" in text:
            sort_by = "Earliest Departure"

        # Time filter
        time_filter = None
        if "morning" in text:
            time_filter = "Morning (05:00 - 11:59)"
        elif "evening" in text or "night" in text:
            time_filter = "Evening/Night (17:00 - 23:59)"
        elif "afternoon" in text:
            time_filter = "Afternoon (12:00 - 16:59)"

        # Budget extraction if mentioned
        budget_match = re.search(r'(?:under|below|budget)\s*(?:₹|rs\.?|inr)?\s*(\d+)', text)
        max_budget = int(budget_match.group(1)) if budget_match else None

        return {
            "query": user_query,
            "detected_src": src_code,
            "detected_src_name": self.dm.code_to_name.get(src_code, src_candidate),
            "detected_dst": dst_code,
            "detected_dst_name": self.dm.code_to_name.get(dst_code, dst_candidate),
            "sort_by": sort_by,
            "time_filter": time_filter,
            "max_budget": max_budget,
            "confidence": "HIGH" if (src_code and dst_code) else ("MEDIUM" if (src_code or dst_code) else "LOW")
        }

    def _resolve_station(self, text_token):
        if not text_token:
            return None
        token = text_token.strip().lower()
        # Direct match
        if token in self.keywords_to_code:
            return self.keywords_to_code[token]
        # Partial match
        for kw, code in self.keywords_to_code.items():
            if token in kw or kw in token:
                return code
        return None
