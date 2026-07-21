"""
Daily Risk Trend Check-In
Multiple check-ins per day — 24-hour database
"""

import streamlit as st
from datetime import datetime, date
from auth import db, get_user_data, update_user_data

# ============================================
# SCORING — plain rules, not a model
# ============================================
SLEEP_SCORES = {"Good": 0, "OK": 1, "Poor": 2}
ENERGY_SCORES = {"Good": 0, "OK": 1, "Low": 2}
SYMPTOM_SCORE = 3

def compute_risk_score(sleep_quality: str, energy_level: str, symptoms_today: bool):
    breakdown = {
        "Sleep": SLEEP_SCORES.get(sleep_quality, 1),
        "Energy": ENERGY_SCORES.get(energy_level, 1),
        "Symptoms": SYMPTOM_SCORE if symptoms_today else 0,
    }
    score = sum(breakdown.values())

    if score <= 1:
        risk_level = "Low"
    elif score <= 3:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return score, risk_level, breakdown

# ============================================
# DATABASE FUNCTIONS
# ============================================
def _today_str():
    return date.today().isoformat()

def get_today_checkins(user_id: str):
    """Get ALL check-ins for today (not just one)"""
    try:
        result = db.child("daily_checkins").child(user_id).order_by_key().get()
        if result and result.val():
            today_checkins = []
            for key, val in result.val().items():
                if isinstance(val, dict) and val.get("date") == _today_str():
                    today_checkins.append({
                        "id": key,
                        "timestamp": val.get("timestamp"),
                        "time": val.get("time", ""),
                        "sleep_quality": val.get("sleep_quality", ""),
                        "energy_level": val.get("energy_level", ""),
                        "symptoms_today": val.get("symptoms_today", False),
                        "symptom_note": val.get("symptom_note", ""),
                        "score": val.get("score", 0),
                        "risk_level": val.get("risk_level", "Low"),
                        "breakdown": val.get("breakdown", {})
                    })
            return sorted(today_checkins, key=lambda x: x.get("timestamp", ""))
        return []
    except Exception as e:
        print(f"Error getting check-ins: {e}")
        return []

def save_checkin(user_id: str, sleep_quality: str, energy_level: str,
                  symptoms_today: bool, symptom_note: str = ""):
    """Saves a check-in and updates user's risk_level"""
    score, risk_level, breakdown = compute_risk_score(sleep_quality, energy_level, symptoms_today)

    checkin_data = {
        "date": _today_str(),
        "timestamp": str(datetime.now()),
        "time": datetime.now().strftime("%H:%M"),
        "sleep_quality": sleep_quality,
        "energy_level": energy_level,
        "symptoms_today": symptoms_today,
        "symptom_note": symptom_note,
        "score": score,
        "risk_level": risk_level,
        "breakdown": breakdown,
    }

    try:
        db.child("daily_checkins").child(user_id).push(checkin_data)
        update_user_data(user_id, {"risk_level": risk_level})
        return True, checkin_data
    except Exception as e:
        print(f"Error saving check-in: {e}")
        return False, None

def get_checkin_history(user_id: str, days: int = 7):
    try:
        result = db.child("daily_checkins").child(user_id).order_by_key().limit_to_last(days*3).get()
        if result and result.val():
            history = []
            for key, val in result.val().items():
                if isinstance(val, dict):
                    history.append({"id": key, **val})
            return sorted(history, key=lambda x: x.get("timestamp", ""))
        return []
    except Exception:
        return []

# ============================================
# STREAMLIT UI
# ============================================
def daily_checkin_ui(user_id: str):
    """Renders the daily check-in card — available ANY TIME the user logs in"""
    today_checkins = get_today_checkins(user_id)

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("📋 How are you feeling right now?")

    # Show today's check-in history
    if today_checkins:
        st.markdown(f'<div class="checkin-history">📊 You\'ve checked in <strong>{len(today_checkins)}</strong> time(s) today.</div>', unsafe_allow_html=True)
        for checkin in today_checkins[-5:]:  # Show last 5
            time_str = checkin.get("time", checkin.get("timestamp", "")[11:16] if checkin.get("timestamp") else "?")
            status_icon = "✅" if checkin.get("risk_level") == "Low" else "⚠️"
            risk_display = checkin.get("risk_level", "Low")
            st.caption(f"  {time_str} {status_icon} {risk_display}")
    else:
        st.caption("💡 No check-ins yet today. How are you feeling?")

    st.markdown("---")

    # Check-in form
    sleep_options = ["Good", "OK", "Poor"]
    energy_options = ["Good", "OK", "Low"]

    col1, col2 = st.columns(2)
    with col1:
        sleep_quality = st.radio(
            "😴 Sleep last night", sleep_options,
            index=0, horizontal=True, key="checkin_sleep"
        )
    with col2:
        energy_level = st.radio(
            "⚡ Energy today", energy_options,
            index=0, horizontal=True, key="checkin_energy"
        )

    symptoms_today = st.checkbox(
        "⚠️ Any unusual symptoms today (aura, dizziness, confusion, etc.)",
        key="checkin_symptoms"
    )
    symptom_note = ""
    if symptoms_today:
        symptom_note = st.text_input(
            "Optional: describe briefly",
            key="checkin_symptom_note"
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ I'm Good", use_container_width=True, key="checkin_good"):
            success, result = save_checkin(user_id, sleep_quality, energy_level, symptoms_today, symptom_note)
            if success:
                st.success(f"✅ Check-in recorded at {datetime.now().strftime('%H:%M')} — today's trend: {result['risk_level']}")
                
                # ✅ KEEP MONITORING ACTIVE
                if 'coverage_tracker' in st.session_state:
                    st.session_state.coverage_tracker.update_activity(
                        motion_detected=True,
                        charging=False,
                        screen_on=True,
                        app_foreground=True
                    )
                
                st.rerun()
            else:
                st.error("❌ Couldn't save check-in.")

    with col2:
        if st.button("⚠️ Not Feeling Well", use_container_width=True, key="checkin_not_well"):
            success, result = save_checkin(user_id, sleep_quality, energy_level, True, symptom_note)
            if success:
                st.warning(f"⚠️ Caregivers notified — today's trend: {result['risk_level']}")
                
                # ✅ KEEP MONITORING ACTIVE
                if 'coverage_tracker' in st.session_state:
                    st.session_state.coverage_tracker.update_activity(
                        motion_detected=True,
                        charging=False,
                        screen_on=True,
                        app_foreground=True
                    )
                
                # Send notification
                from auth import send_risk_notification
                send_risk_notification(user_id, result['risk_level'])
                st.rerun()
            else:
                st.error("❌ Couldn't save check-in.")

    st.markdown('</div>', unsafe_allow_html=True)