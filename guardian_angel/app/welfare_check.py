"""
Milestone 4 - Intelligent Welfare Check Protocol
Escalates when risk was rising and monitoring stopped
Environment: Local (VS Code)
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class EscalationLevel(Enum):
    NONE = 0
    NOTIFY_USER = 1
    NOTIFY_CAREGIVER = 2
    EMERGENCY_ALERT = 3


@dataclass
class WelfareCheckState:
    risk_trend: List[RiskLevel] = field(default_factory=list)
    monitoring_was_active: bool = True
    last_risk_check: datetime = field(default_factory=datetime.now)
    escalation_level: EscalationLevel = EscalationLevel.NONE


class WelfareCheckProtocol:
    """Handles welfare check logic with escalation"""
    
    def __init__(self):
        self.state = WelfareCheckState()
        self.caregiver_contacts: List[str] = []
        self.user_confirmed_ok = False
        self.escalation_start_time: Optional[datetime] = None
        self.alerts_sent: List[str] = []
        self._notification_callback: Optional[Callable] = None
        
    def set_caregivers(self, contacts: List[str]):
        """Set caregiver contact information"""
        self.caregiver_contacts = contacts
        print(f"✅ Caregivers set: {', '.join(contacts)}")
        
    def set_notification_callback(self, callback: Callable):
        """Set a callback function for sending notifications"""
        self._notification_callback = callback
        
    def update_risk(self, risk: RiskLevel, monitoring_active: bool):
        """Called with latest risk assessment and monitoring status"""
        
        # Track risk trend (last 5 assessments)
        self.state.risk_trend.append(risk)
        if len(self.state.risk_trend) > 5:
            self.state.risk_trend.pop(0)
            
        self.state.monitoring_was_active = monitoring_active
        self.state.last_risk_check = datetime.now()
        
        print(f"📊 Risk updated: {risk.value}, Monitoring: {'ACTIVE' if monitoring_active else 'PAUSED'}")
        print(f"   Risk trend: {[r.value for r in self.state.risk_trend]}")
        
        # Detect: risk was rising AND monitoring just stopped
        if self._detect_risk_rising() and not monitoring_active:
            print("⚠️ RISING RISK + MONITORING STOPPED - Triggering welfare check!")
            self._trigger_welfare_check()
        else:
            # Reset escalation if monitoring resumes or risk drops
            if monitoring_active or not self._detect_risk_rising():
                if self.state.escalation_level != EscalationLevel.NONE:
                    print("✅ Risk dropped or monitoring resumed - Canceling escalation")
                    self.state.escalation_level = EscalationLevel.NONE
                    self.escalation_start_time = None
                    self.user_confirmed_ok = False
                    
    def _detect_risk_rising(self) -> bool:
        """Check if risk level has been trending upward"""
        if len(self.state.risk_trend) < 3:
            return False
            
        # Map risk to numeric values
        risk_values = {"low": 1, "moderate": 2, "high": 3}
        trend = [risk_values[r.value] for r in self.state.risk_trend[-3:]]
        
        # Check if risk has increased or stayed high
        return trend[-1] >= trend[0] and trend[-1] >= 2
        
    def _trigger_welfare_check(self):
        """Start the welfare check escalation protocol"""
        self.escalation_start_time = datetime.now()
        self.state.escalation_level = EscalationLevel.NOTIFY_USER
        self.user_confirmed_ok = False
        print(f"🆘 Welfare check triggered at {self.escalation_start_time.strftime('%H:%M:%S')}")
        
        # Send immediate user notification
        self._send_alert("🔴 Seizure Risk Alert - Are you okay?", "user")
        
    def user_responds_ok(self):
        """User confirms they're fine"""
        self.user_confirmed_ok = True
        self.state.escalation_level = EscalationLevel.NONE
        self.escalation_start_time = None
        self.alerts_sent.append(f"User OK confirmed at {datetime.now()}")
        print("👍 User confirmed OK - Welfare check complete")
        
    def user_responds_help(self):
        """User requests help"""
        self.state.escalation_level = EscalationLevel.EMERGENCY_ALERT
        self._send_alert("🚨 USER REQUESTED HELP - Emergency alert sent!", "emergency")
        
    def _send_alert(self, message: str, recipient_type: str):
        """Send an alert via callback or console"""
        if self._notification_callback:
            self._notification_callback(message, recipient_type)
        else:
            print(f"📢 [{recipient_type.upper()}] {message}")
        self.alerts_sent.append(f"{recipient_type}: {message}")
        
    def get_escalation_action(self) -> Dict:
        """Determine what action to take based on time since welfare check triggered"""
        if self.escalation_start_time is None:
            return {"action": "none", "level": EscalationLevel.NONE, "message": "No active welfare check"}
            
        if self.user_confirmed_ok:
            return {"action": "resolved", "level": EscalationLevel.NONE, "message": "User confirmed OK"}
            
        elapsed = (datetime.now() - self.escalation_start_time).total_seconds()
        
        # Escalation timeline:
        # 0-30s: Notify user (app prompt)
        # 30-60s: Notify caregivers  
        # 60s+: Emergency alert
        
        if elapsed < 10:  # Immediate - quick prompt
            level = EscalationLevel.NOTIFY_USER
            action = "notify_user"
            message = "⚠️ Are you okay? Tap 'I'm fine' to cancel"
            
        elif elapsed < 30:
            level = EscalationLevel.NOTIFY_USER
            action = "notify_user_urgent"
            message = "🚨 RESPOND NOW! Are you okay?"
            
        elif elapsed < 60:
            level = EscalationLevel.NOTIFY_CAREGIVER
            action = "notify_caregivers"
            message = f"📱 Alerting caregivers: {', '.join(self.caregiver_contacts) if self.caregiver_contacts else 'No caregivers set'}"
            if not self._alert_sent_for_level(EscalationLevel.NOTIFY_CAREGIVER):
                self._send_alert("⚠️ Welfare check triggered - User not responding. Please check on them.", "caregiver")
            
        else:
            level = EscalationLevel.EMERGENCY_ALERT
            action = "emergency_alert_with_gps"
            message = "🚨 EMERGENCY ALERT - GPS location sent to emergency contacts"
            if not self._alert_sent_for_level(EscalationLevel.EMERGENCY_ALERT):
                self._send_alert("🚨 EMERGENCY: User unresponsive for 60+ seconds. GPS location shared.", "emergency")
            
        self.state.escalation_level = level
        
        return {
            "action": action,
            "level": level,
            "level_name": level.name,
            "elapsed_seconds": round(elapsed, 1),
            "user_confirmed_ok": self.user_confirmed_ok,
            "caregivers_contacted": self.caregiver_contacts if elapsed > 30 else [],
            "message": message
        }
        
    def _alert_sent_for_level(self, level: EscalationLevel) -> bool:
        """Check if an alert at this level has already been sent"""
        for alert in self.alerts_sent:
            if level.name in alert:
                return True
        return False
    
    def get_summary(self) -> Dict:
        """Get a summary of the current welfare check state"""
        escalation_action = self.get_escalation_action()
        
        return {
            "risk_trend": [r.value for r in self.state.risk_trend],
            "monitoring_active": self.state.monitoring_was_active,
            "welfare_check_active": self.escalation_start_time is not None,
            "user_confirmed_ok": self.user_confirmed_ok,
            "escalation_level": self.state.escalation_level.name,
            "elapsed_since_trigger": round((datetime.now() - self.escalation_start_time).total_seconds(), 1) if self.escalation_start_time else 0,
            "current_action": escalation_action,
            "alerts_sent": len(self.alerts_sent)
        }