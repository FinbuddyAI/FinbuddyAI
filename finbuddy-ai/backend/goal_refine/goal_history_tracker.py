import pandas as pd
import json
import os
from datetime import datetime
import uuid
import openai
import numpy as np
from typing import List

class GoalHistoryTracker:
    """Goal adjustment history tracker"""
    
    def __init__(self, history_file="./data/goal_adjustment_history.json"):
        """Initialize history tracker"""
        self.history_file = history_file
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Ensure history file exists"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
    
    def load_history(self):
        """Load adjustment history"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history
        except (json.JSONDecodeError, FileNotFoundError):
            # Return empty list if file doesn't exist or is malformed
            return []
    
    def save_adjustment(self, original_goals, adjusted_goals, adjustment_result, trigger_event=None):
        """
        Save goal adjustment record
        
        Args:
            original_goals: Original goals as DataFrame or list of dicts
            adjusted_goals: Adjusted goals as DataFrame or list of dicts
            adjustment_result: Adjustment result dictionary
            trigger_event: Description of event that triggered the adjustment
        
        Returns:
            adjustment_id: Unique ID of the adjustment record
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(original_goals, pd.DataFrame):
            original_goals = original_goals.to_dict('records')
        if isinstance(adjusted_goals, pd.DataFrame):
            adjusted_goals = adjusted_goals.to_dict('records')
        
        # Generate unique ID
        adjustment_id = str(uuid.uuid4())
        
        # Create adjustment record
        adjustment_record = {
            'id': adjustment_id,
            'timestamp': datetime.now().isoformat(),
            'original_goals': original_goals,
            'adjusted_goals': adjusted_goals,
            'adjustment_details': {
                'summary': adjustment_result.get('summary', ''),
                'adjustments': adjustment_result.get('adjustments', {}),
                'recommendations': adjustment_result.get('recommendations', [])
            },
            'trigger_event': trigger_event or 'Scheduled adjustment'
        }
        
        # Load existing history
        history = self.load_history()
        
        # Add new record
        history.append(adjustment_record)
        
        # Save updated history
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        
        return adjustment_id
    
    def get_adjustment_by_id(self, adjustment_id):
        """Get adjustment record by ID"""
        history = self.load_history()
        for record in history:
            if record['id'] == adjustment_id:
                return record
        return None
    
    def get_active_goals(self):
        """
        Get current active goals (latest uncancelled adjustment)
        
        Returns:
            Latest active goals list, or None if none exist
        """
        history = self.load_history()
        
        if not history:
            return None
        
        # Sort by timestamp descending
        sorted_history = sorted(
            history, 
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        # Find latest uncancelled record
        for record in sorted_history:
            if not record.get('cancelled', False):
                return record['adjusted_goals']
        
        # If all records are cancelled, return oldest original goals
        if sorted_history:
            oldest_record = sorted(history, key=lambda x: x.get('timestamp', ''))[0]
            return oldest_record['original_goals']
        
        return None
    
    def get_adjustment_summary(self, limit=10):
        """
        Get adjustment history summary
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of adjustment history summaries
        """
        history = self.load_history()
        
        # Sort by timestamp descending
        sorted_history = sorted(
            history, 
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        # Create summaries
        summaries = []
        for record in sorted_history[:limit]:
            timestamp = datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            
            # Calculate changes
            changes = []
            for orig, adj in zip(record['original_goals'], record['adjusted_goals']):
                if orig['category'] == adj['category']:
                    diff = adj['target_amount'] - orig['target_amount']
                    if abs(diff) > 0.01:  # Ignore tiny changes
                        change_pct = (diff / orig['target_amount']) * 100
                        change_str = f"{orig['category']}: {diff:+.2f} ({change_pct:+.1f}%)"
                        changes.append(change_str)
            
            summaries.append({
                'id': record['id'],
                'timestamp': timestamp,
                'trigger_event': record.get('trigger_event', 'Scheduled adjustment'),
                'summary': record['adjustment_details']['summary'],
                'key_changes': changes,
                'cancelled': record.get('cancelled', False)
            })
        
        return summaries

    def _save_history(self, history):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        