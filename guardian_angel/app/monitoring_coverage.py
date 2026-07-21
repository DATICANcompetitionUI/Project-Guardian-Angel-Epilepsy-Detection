"""
Milestone 4 - Smart Monitoring Coverage
Tracks when monitoring is actually working vs paused
Environment: Local (VS Code)
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


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
    """Tracks monitoring coverage over time"""
    
    def __init__(self):
        self.sessions: List[MonitoringSession] = []
        self.current_session: Optional[MonitoringSession] = None
        self.last_activity = datetime.now()
        self.total_active_seconds = 0
        self.total_paused_seconds = 0
        
    def update_activity(self, motion_detected: bool, charging: bool, screen_on: bool, app_foreground: bool = True):
        """
        Called periodically with current phone state
        
        Args:
            motion_detected: Is the phone detecting motion (from accelerometer)
            charging: Is the phone plugged in
            screen_on: Is the screen on
            app_foreground: Is the app in foreground
        """
        now = datetime.now()
        self.last_activity = now
        
        # Determine if monitoring should be active
        # Monitoring is active if: app is foreground AND (motion detected OR screen is on)
        should_be_active = app_foreground and (motion_detected or screen_on)
        
        if should_be_active and self.current_session is None:
            # Start new monitoring session
            self.current_session = MonitoringSession(start_time=now)
            self.sessions.append(self.current_session)
            print(f"[{now.strftime('%H:%M:%S')}] Monitoring ACTIVE")
            
        elif not should_be_active and self.current_session is not None:
            # End current monitoring session
            if self.current_session.end_time is None:
                self.current_session.end_time = now
                duration = (now - self.current_session.start_time).total_seconds()
                self.total_active_seconds += duration
                self.current_session.reason_paused = self._get_pause_reason(motion_detected, charging, screen_on, app_foreground)
            self.current_session = None
            print(f"[{now.strftime('%H:%M:%S')}] Monitoring PAUSED")
    
    def _get_pause_reason(self, motion_detected: bool, charging: bool, screen_on: bool, app_foreground: bool) -> str:
        """Determine why monitoring was paused"""
        if not app_foreground:
            return "app_background"
        elif not motion_detected and not screen_on:
            return "no_activity"
        elif charging:
            return "charging"
        else:
            return "unknown"
    
    def get_coverage_percentage(self, period_hours: int = 24) -> float:
        """Calculate what % of last N hours had active monitoring"""
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
        """Return current monitoring status and daily coverage"""
        now = datetime.now()
        is_active = self.current_session is not None
        
        report = {
            "status": "ACTIVE" if is_active else "PAUSED",
            "status_icon": "🟢" if is_active else "🔴",
            "current_session_start": self.current_session.start_time.strftime("%H:%M:%S") if self.current_session else None,
            "daily_coverage_percent": round(self.get_coverage_percentage(24), 1),
            "sessions_today": len([s for s in self.sessions if s.start_time.date() == now.date()]),
            "last_activity": self.last_activity.strftime("%H:%M:%S"),
            "total_active_today_seconds": self.total_active_seconds,
            "total_paused_today_seconds": self.total_paused_seconds
        }
        
        return report
    
    def get_recent_sessions(self, count: int = 5) -> List[Dict]:
        """Get the most recent monitoring sessions"""
        sessions = sorted(self.sessions, key=lambda s: s.start_time, reverse=True)[:count]
        
        result = []
        for s in sessions:
            duration = "ongoing" if s.end_time is None else f"{(s.end_time - s.start_time).total_seconds():.0f}s"
            result.append({
                "start": s.start_time.strftime("%H:%M:%S"),
                "end": s.end_time.strftime("%H:%M:%S") if s.end_time else "ongoing",
                "duration": duration,
                "status": s.status.value,
                "reason": s.reason_paused or "active"
            })
        return result