"""
Database - Store User Risk, Alerts, and Settings
"""

import firebase_admin
from firebase_admin import credentials, db
import json
from datetime import datetime

class UserDatabase:
    def __init__(self):
        self.users_ref = db.reference('users')
        self.alerts_ref = db.reference('alerts')
        self.settings_ref = db.reference('settings')
    
    def save_user_data(self, user_id, data):
        """Save user risk, contacts, monitoring data"""
        self.users_ref.child(user_id).update({
            "risk_level": data.get("risk_level", "Low"),
            "monitoring_active": data.get("monitoring_active", True),
            "contacts": data.get("contacts", []),
            "last_updated": str(datetime.now())
        })
    
    def save_alert(self, user_id, alert_data):
        """Save seizure alert to database"""
        self.alerts_ref.child(user_id).push({
            "timestamp": str(datetime.now()),
            "risk": alert_data.get("risk", "HIGH"),
            "confidence": alert_data.get("confidence", 0.0),
            "location": alert_data.get("location", "N/A"),
            "resolved": alert_data.get("resolved", False)
        })
    
    def get_user_alerts(self, user_id, limit=20):
        """Get recent alerts for a user"""
        alerts = self.alerts_ref.child(user_id).order_by_key().limit_to_last(limit).get()
        if alerts:
            return [{"id": key, **val} for key, val in alerts.items()]
        return []
    
    def get_user_settings(self, user_id):
        """Get user settings"""
        settings = self.settings_ref.child(user_id).get()
        return settings if settings else {}
    
    def update_user_settings(self, user_id, settings):
        """Update user settings"""
        self.settings_ref.child(user_id).update(settings)