import pandas as pd
import json
from datetime import datetime
import uuid
import openai
import numpy as np
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class GoalHistoryTracker:
    """Goal adjustment history tracker"""
    
    def __init__(self):
        """Initialize history tracker"""
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url)
    
    def save_adjustment(self, user_id: int, original_goals, adjusted_goals, adjustment_result, trigger_event=None):
        """
        Save goal adjustment record
        
        Args:
            user_id: User ID
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
            
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Insert adjustment record
            cur.execute("""
                INSERT INTO goal_adjustments 
                (user_id, timestamp, trigger_event, original_goals, adjusted_goals, adjustment_details)
                VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_id,
                trigger_event or "Scheduled adjustment",
                json.dumps(original_goals),
                json.dumps(adjusted_goals),
                json.dumps(adjustment_result)
            ))
            
            adjustment_id = cur.fetchone()['id']
            conn.commit()
            return adjustment_id
            
        finally:
            cur.close()
            conn.close()
    
    def get_adjustment_summary(self, user_id: int, limit=10):
        """
        Get adjustment history summary for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List of adjustment history summaries
        """
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Get recent adjustments
            cur.execute("""
                SELECT id, timestamp, trigger_event, original_goals, adjusted_goals, 
                       adjustment_details, cancelled
                FROM goal_adjustments 
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (user_id, limit))
            
            records = cur.fetchall()
            
            # Create summaries
            summaries = []
            for record in records:
                # Calculate changes
                changes = []
                original_goals = record['original_goals']
                adjusted_goals = record['adjusted_goals']
                
                for orig, adj in zip(original_goals, adjusted_goals):
                    if orig['category'] == adj['category']:
                        diff = adj['target_amount'] - orig['target_amount']
                        if abs(diff) > 0.01:  # Ignore tiny changes
                            change_pct = (diff / orig['target_amount']) * 100
                            change_str = f"{orig['category']}: {diff:+.2f} ({change_pct:+.1f}%)"
                            changes.append(change_str)
                
                summaries.append({
                    'id': record['id'],
                    'timestamp': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'trigger_event': record['trigger_event'],
                    'summary': record['adjustment_details'].get('summary', ''),
                    'key_changes': changes,
                    'cancelled': record['cancelled']
                })
            
            return summaries
            
        finally:
            cur.close()
            conn.close()
    
    def get_adjustment_by_id(self, adjustment_id: int):
        """Get adjustment record by ID"""
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("""
                SELECT * FROM goal_adjustments WHERE id = %s
            """, (adjustment_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

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

    def _save_history(self, history):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        