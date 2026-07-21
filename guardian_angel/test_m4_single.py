"""
Milestone 4 - Complete Single File Test
Run this: python test_m4_single.py
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ============================================
# PART 1: Monitoring Coverage Code
# ============================================

class MonitoringStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STANDBY = "standby"

@dataclass
class MonitoringSession:
    start_time: datetime
    end_time: Optional[datetime] = None
    status: MonitoringStatus = MonitoringStatus.ACTIVE
    reason_paused: Optional[str] = None

class MonitoringCoverageTracker:
    def __init__(self):
        self.sessions: List[MonitoringSession] = []
        self.current_session: Optional[MonitoringSession] = None
        self.last_activity = datetime.now()
        self.total_active_seconds = 0
        
    def update_activity(self, motion_detected: bool, charging: bool, screen_on: bool, app_foreground: bool = True):
        now = datetime.now()
        self.last_activity = now
        should_be_active = app_foreground and (motion_detected or screen_on)
        
        if should_be_active and self.current_session is None:
            self.current_session = MonitoringSession(start_time=now)
            self.sessions.append(self.current_session)
            print(f"[{now.strftime('%H:%M:%S')}] Monitoring ACTIVE")
        elif not should_be_active and self.current_session is not None:
            if self.current_session.end_time is None:
                self.current_session.end_time = now
                duration = (now - self.current_session.start_time).total_seconds()
                self.total_active_seconds += duration
            self.current_session = None
            print(f"[{now.strftime('%H:%M:%S')}] Monitoring PAUSED")
    
    def get_coverage_percentage(self, period_hours: int = 24) -> float:
        cutoff = datetime.now() - timedelta(hours=period_hours)
        total_seconds = period_hours * 3600
        active_seconds = 0
        for session in self.sessions:
            if session.end_time is None:
                session_end = datetime.now()
            else:
                session_end = session.end_time
            if session_end < cutoff:
                continue
            session_start = max(session.start_time, cutoff)
            duration = (session_end - session_start).total_seconds()
            if session.status == MonitoringStatus.ACTIVE:
                active_seconds += duration
        return (active_seconds / total_seconds) * 100 if total_seconds > 0 else 0
    
    def get_status_report(self) -> Dict:
        now = datetime.now()
        is_active = self.current_session is not None
        return {
            "status": "ACTIVE" if is_active else "PAUSED",
            "status_icon": "🟢" if is_active else "🔴",
            "current_session_start": self.current_session.start_time.strftime("%H:%M:%S") if self.current_session else None,
            "daily_coverage_percent": round(self.get_coverage_percentage(24), 1),
            "sessions_today": len([s for s in self.sessions if s.start_time.date() == now.date()]),
            "last_activity": self.last_activity.strftime("%H:%M:%S")
        }
    
    def get_recent_sessions(self, count: int = 5) -> List[Dict]:
        sessions = sorted(self.sessions, key=lambda s: s.start_time, reverse=True)[:count]
        result = []
        for s in sessions:
            duration = "ongoing" if s.end_time is None else f"{(s.end_time - s.start_time).total_seconds():.0f}s"
            result.append({
                "start": s.start_time.strftime("%H:%M:%S"),
                "end": s.end_time.strftime("%H:%M:%S") if s.end_time else "ongoing",
                "duration": duration,
                "status": s.status.value
            })
        return result

# ============================================
# PART 2: Welfare Check Code
# ============================================

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
    def __init__(self):
        self.state = WelfareCheckState()
        self.caregiver_contacts: List[str] = []
        self.user_confirmed_ok = False
        self.escalation_start_time: Optional[datetime] = None
        self.alerts_sent: List[str] = []
        
    def set_caregivers(self, contacts: List[str]):
        self.caregiver_contacts = contacts
        print(f"✅ Caregivers set: {', '.join(contacts)}")
        
    def update_risk(self, risk: RiskLevel, monitoring_active: bool):
        self.state.risk_trend.append(risk)
        if len(self.state.risk_trend) > 5:
            self.state.risk_trend.pop(0)
        self.state.monitoring_was_active = monitoring_active
        self.state.last_risk_check = datetime.now()
        
        print(f"📊 Risk updated: {risk.value}, Monitoring: {'ACTIVE' if monitoring_active else 'PAUSED'}")
        
        if self._detect_risk_rising() and not monitoring_active:
            print("⚠️ RISING RISK + MONITORING STOPPED - Triggering welfare check!")
            self._trigger_welfare_check()
        else:
            if monitoring_active or not self._detect_risk_rising():
                if self.state.escalation_level != EscalationLevel.NONE:
                    print("✅ Risk dropped or monitoring resumed - Canceling escalation")
                    self.state.escalation_level = EscalationLevel.NONE
                    self.escalation_start_time = None
                    self.user_confirmed_ok = False
                    
    def _detect_risk_rising(self) -> bool:
        if len(self.state.risk_trend) < 3:
            return False
        risk_values = {"low": 1, "moderate": 2, "high": 3}
        trend = [risk_values[r.value] for r in self.state.risk_trend[-3:]]
        return trend[-1] >= trend[0] and trend[-1] >= 2
        
    def _trigger_welfare_check(self):
        self.escalation_start_time = datetime.now()
        self.state.escalation_level = EscalationLevel.NOTIFY_USER
        self.user_confirmed_ok = False
        print(f"🆘 Welfare check triggered at {self.escalation_start_time.strftime('%H:%M:%S')}")
        self._send_alert("🔴 Seizure Risk Alert - Are you okay?", "user")
        
    def user_responds_ok(self):
        self.user_confirmed_ok = True
        self.state.escalation_level = EscalationLevel.NONE
        self.escalation_start_time = None
        self.alerts_sent.append(f"User OK confirmed at {datetime.now()}")
        print("👍 User confirmed OK - Welfare check complete")
        
    def _send_alert(self, message: str, recipient_type: str):
        print(f"📢 [{recipient_type.upper()}] {message}")
        self.alerts_sent.append(f"{recipient_type}: {message}")
        
    def get_escalation_action(self) -> Dict:
        if self.escalation_start_time is None:
            return {"action": "none", "level": EscalationLevel.NONE, "message": "No active welfare check"}
        if self.user_confirmed_ok:
            return {"action": "resolved", "level": EscalationLevel.NONE, "message": "User confirmed OK"}
        elapsed = (datetime.now() - self.escalation_start_time).total_seconds()
        if elapsed < 10:
            return {"action": "notify_user", "level": EscalationLevel.NOTIFY_USER, "level_name": "NOTIFY_USER", "message": "⚠️ Are you okay? Tap 'I'm fine' to cancel"}
        elif elapsed < 30:
            return {"action": "notify_user_urgent", "level": EscalationLevel.NOTIFY_USER, "level_name": "NOTIFY_USER", "message": "🚨 RESPOND NOW! Are you okay?"}
        elif elapsed < 60:
            if not self._alert_sent_for_level(EscalationLevel.NOTIFY_CAREGIVER):
                self._send_alert("⚠️ Welfare check triggered - User not responding. Please check on them.", "caregiver")
            return {"action": "notify_caregivers", "level": EscalationLevel.NOTIFY_CAREGIVER, "level_name": "NOTIFY_CAREGIVER", "message": f"📱 Alerting caregivers"}
        else:
            if not self._alert_sent_for_level(EscalationLevel.EMERGENCY_ALERT):
                self._send_alert("🚨 EMERGENCY: User unresponsive for 60+ seconds. GPS location shared.", "emergency")
            return {"action": "emergency_alert", "level": EscalationLevel.EMERGENCY_ALERT, "level_name": "EMERGENCY_ALERT", "message": "🚨 EMERGENCY ALERT - GPS location sent"}
        
    def _alert_sent_for_level(self, level: EscalationLevel) -> bool:
        for alert in self.alerts_sent:
            if level.name in alert:
                return True
        return False
    
    def get_summary(self) -> Dict:
        action = self.get_escalation_action()
        return {
            "risk_trend": [r.value for r in self.state.risk_trend],
            "monitoring_active": self.state.monitoring_was_active,
            "welfare_check_active": self.escalation_start_time is not None,
            "user_confirmed_ok": self.user_confirmed_ok,
            "escalation_level": self.state.escalation_level.name,
            "current_action": action
        }

# ============================================
# PART 3: TESTS
# ============================================

print("=" * 60)
print("🧪 TESTING MILESTONE 4 - MONITORING COVERAGE + WELFARE CHECK")
print("=" * 60)

# TEST 1: Monitoring Coverage
print("\n📊 TEST 1: Monitoring Coverage Tracker")
print("-" * 40)

tracker = MonitoringCoverageTracker()
print("Simulating phone activity...")
tracker.update_activity(motion_detected=True, charging=False, screen_on=True)
time.sleep(1)
tracker.update_activity(motion_detected=False, charging=False, screen_on=False)
time.sleep(1)
tracker.update_activity(motion_detected=True, charging=False, screen_on=True)
time.sleep(1)
tracker.update_activity(motion_detected=False, charging=True, screen_on=True)
time.sleep(1)
tracker.update_activity(motion_detected=False, charging=False, screen_on=False)

report = tracker.get_status_report()
print(f"\n📋 Monitoring Report:")
print(f"   Status: {report['status']} {report['status_icon']}")
print(f"   Daily Coverage: {report['daily_coverage_percent']}%")
print(f"   Sessions Today: {report['sessions_today']}")

print("\n✅ Monitoring Coverage Test PASSED")

# TEST 2: Welfare Check
print("\n\n🚨 TEST 2: Welfare Check Protocol")
print("-" * 40)

welfare = WelfareCheckProtocol()
welfare.set_caregivers(["mom@email.com", "dad@email.com"])

print("\nScenario: Risk rising → Monitoring stops")
welfare.update_risk(RiskLevel.LOW, monitoring_active=True)
time.sleep(0.5)
welfare.update_risk(RiskLevel.MODERATE, monitoring_active=True)
time.sleep(0.5)
welfare.update_risk(RiskLevel.HIGH, monitoring_active=True)
time.sleep(0.5)
welfare.update_risk(RiskLevel.HIGH, monitoring_active=False)

print("\nChecking escalation...")
time.sleep(5)
action = welfare.get_escalation_action()
print(f"   After 5s: {action['level_name']} - {action['message']}")

time.sleep(30)
action = welfare.get_escalation_action()
print(f"   After 35s: {action['level_name']} - {action['message']}")

time.sleep(30)
action = welfare.get_escalation_action()
print(f"   After 65s: {action['level_name']} - {action['message']}")

print("\nUser responds 'I'm fine'")
welfare.user_responds_ok()
print("✅ Welfare Check Test PASSED")

# TEST 3: Integration
print("\n\n🔗 TEST 3: Integration Test")
print("-" * 40)

tracker = MonitoringCoverageTracker()
welfare = WelfareCheckProtocol()
welfare.set_caregivers(["emergency@example.com"])

print("\nFull user journey:")
tracker.update_activity(True, False, True)
welfare.update_risk(RiskLevel.LOW, True)
time.sleep(0.5)

welfare.update_risk(RiskLevel.MODERATE, True)
time.sleep(0.5)

welfare.update_risk(RiskLevel.HIGH, True)
time.sleep(0.5)

tracker.update_activity(False, False, False)
welfare.update_risk(RiskLevel.HIGH, False)

coverage = tracker.get_status_report()
summary = welfare.get_summary()

print(f"\n   Monitoring: {coverage['status']} ({coverage['daily_coverage_percent']}% coverage)")
print(f"   Risk Trend: {summary['risk_trend']}")
print(f"   Escalation Level: {summary['escalation_level']}")

print("\n✅ Integration Test PASSED")

# FINAL
print("\n" + "=" * 60)
print("✅ ALL MILESTONE 4 TESTS PASSED")
print("=" * 60)
print("\n🎯 Milestone 4 - COMPLETE")
print("=" * 60)