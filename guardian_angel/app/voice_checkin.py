"""
Daily Voice Check-In System - IVR for Users Without Smartphones
Uses Twilio Voice API (Free Trial)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from auth import db, get_user_data, update_user_data
from admin_dashboard import inject_css, pulse_divider, render_table, pill, metric_card

# ============================================
# TWILIO VOICE CONFIGURATION
# Credentials are pulled from Streamlit secrets (.streamlit/secrets.toml
# or the Streamlit Cloud "Secrets" panel) — never hardcode real SIDs/tokens
# in source, since anything committed or pasted becomes effectively public.
#
# secrets.toml:
# [twilio]
# account_sid = "..."
# auth_token = "..."
# phone_number = "+1234567890"
# webhook_url = "https://your-ngrok-url.ngrok.io/voice_checkin"
# ============================================

def get_twilio_config():
    try:
        return {
            "account_sid": st.secrets["twilio"]["account_sid"],
            "auth_token": st.secrets["twilio"]["auth_token"],
            "phone_number": st.secrets["twilio"]["phone_number"],
            "webhook_url": st.secrets["twilio"].get("webhook_url", ""),
        }
    except Exception:
        return None


# ============================================
# DATABASE FUNCTIONS
# ============================================

def log_checkin_response(user_id, response, call_sid, caller_type="patient"):
    """Log user's response from IVR"""
    try:
        db.child("voice_checkins").child(user_id).push({
            "timestamp": str(datetime.now()),
            "call_sid": call_sid,
            "response": response,
            "caller_type": caller_type,
            "date": str(datetime.now().date())
        })

        if response == "help":
            update_user_data(user_id, {
                "risk_level": "Moderate",
                "last_checkin": str(datetime.now()),
                "checkin_status": "help"
            })
        else:
            update_user_data(user_id, {
                "risk_level": "Low",
                "last_checkin": str(datetime.now()),
                "checkin_status": "fine"
            })

        return True
    except Exception as e:
        print(f"Error logging check-in: {e}")
        return False


def get_checkin_history(user_id, days=7):
    """Get check-in history for the last N days"""
    try:
        checkins = db.child("voice_checkins").child(user_id).order_by_key().limit_to_last(days * 2).get()
        if checkins and checkins.val():
            history = []
            for key, val in checkins.val().items():
                if isinstance(val, dict):
                    history.append({
                        "date": val.get("date", ""),
                        "time": val.get("timestamp", ""),
                        "response": val.get("response", "unknown"),
                        "caller_type": val.get("caller_type", "patient")
                    })
            return history
        return []
    except Exception:
        return []


def get_users_for_checkin():
    """Get all users who have check-in enabled"""
    try:
        users_data = db.child("users").get().val()
        if not users_data:
            return []

        users = []
        for uid, data in users_data.items():
            if isinstance(data, dict):
                settings = data.get("settings", {})
                checkin_time = settings.get("checkin_time", "09:00")
                phone = data.get("phone")

                if phone:
                    users.append({
                        "id": uid,
                        "name": data.get("name", "User"),
                        "phone": phone,
                        "checkin_time": checkin_time
                    })
        return users
    except Exception:
        return []


# ============================================
# STYLE HELPERS
# ============================================

def response_pill(text):
    kind = "high" if "Help" in text or "🆘" in text else "active"
    return pill(text, kind)


def caller_pill(text):
    kind = "caregiver" if text.lower() == "caregiver" else "user"
    return pill(text, kind)


# ============================================
# STREAMLIT UI
# ============================================

def voice_checkin_dashboard():
    """Admin dashboard for voice check-ins"""
    inject_css()  # safe to call again if admin_dashboard() already ran this session

    st.markdown("""
        <div class="ga-topbar">
            <div>
                <h2>📞 Daily Voice Check-In</h2>
                <p>IVR check-ins for users without a smartphone</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    pulse_divider()

    twilio_config = get_twilio_config()
    if not twilio_config:
        st.markdown(
            '<div class="empty-box">⚠️ Twilio isn\'t configured yet. Add <code>account_sid</code>, '
            '<code>auth_token</code>, <code>phone_number</code>, and <code>webhook_url</code> under a '
            '<code>[twilio]</code> section in your Streamlit secrets to enable live calling.</div>',
            unsafe_allow_html=True
        )

    display_number = twilio_config["phone_number"] if twilio_config else "+1 234 567 8900"
    st.markdown(f"""
    <div class="info-box">
        📞 <strong>Voice Check-In Number:</strong> {display_number} — No smartphone? No problem!
        Call this number for daily check-ins. Caregivers can call too!
    </div>
    """, unsafe_allow_html=True)

    st.info("""
    **How it works:**
    1. 📞 **Users call the number** — No smartphone needed
    2. 🗣️ **IVR asks:** "Are you the patient or caregiver?"
    3. 🔢 **Press 1** (Patient) → Daily check-in
    4. 🔢 **Press 2** (Caregiver) → Report on behalf of patient
    5. ✅ **Press 1** → "I'm fine" (logged in system)
    6. 🆘 **Press 2** → "I need help" (caregivers alerted)
    """)

    # ---------- Metrics ----------
    metrics_html = '<div class="metric-grid">'
    metrics_html += metric_card("Daily Check-Ins", "12", "📞")
    metrics_html += metric_card("Fine Responses", "10", "✅", "good")
    metrics_html += metric_card("Help Requests", "2", "🆘", "alert")
    metrics_html += metric_card("Auto-Calls Scheduled", "5", "⏳")
    metrics_html += '</div>'
    st.markdown(metrics_html, unsafe_allow_html=True)

    # ---------- Auto-call schedule ----------
    st.markdown('<div class="section-title">⏰ Auto-Call Schedule</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        checkin_time = st.time_input("Daily Check-In Time", value=time(9, 0))
        st.caption("📞 Users will receive a call at this time daily")

    with col2:
        st.write("")
        if st.button("🔄 Update Schedule", use_container_width=True):
            st.success(f"✅ Auto-call schedule updated to {checkin_time.strftime('%H:%M')}")

    # ---------- Check-in history ----------
    st.markdown('<div class="section-title">📋 Recent Check-In History</div>', unsafe_allow_html=True)

    history_data = [
        {"date": "2026-07-16", "user": "john doe", "response": "✅ Fine", "caller": "Patient"},
        {"date": "2026-07-16", "user": "sarah smith", "response": "🆘 Help", "caller": "Caregiver"},
        {"date": "2026-07-15", "user": "mike johnson", "response": "✅ Fine", "caller": "Patient"},
    ]
    df = pd.DataFrame(history_data)
    render_table(df, [
        ("date", "Date", None),
        ("user", "User", None),
        ("response", "Response", response_pill),
        ("caller", "Caller", caller_pill),
    ])

    # ---------- Test call ----------
    st.markdown('<div class="section-title">📞 Test Call</div>', unsafe_allow_html=True)
    test_phone = st.text_input("Test Phone Number", placeholder="+234 800 000 0000")
    if st.button("📞 Make Test Call", use_container_width=True):
        if not test_phone:
            st.warning("⚠️ Please enter a phone number.")
        elif not twilio_config:
            st.warning("⚠️ Twilio isn't configured — add your credentials to secrets first.")
        elif not twilio_config.get("webhook_url"):
            st.warning("⚠️ No `webhook_url` set under `[twilio]` in secrets — Twilio needs a URL to fetch call instructions from (e.g. your ngrok tunnel).")
        else:
            try:
                from twilio.rest import Client

                client = Client(twilio_config["account_sid"], twilio_config["auth_token"])

                call = client.calls.create(
                    url=twilio_config["webhook_url"],
                    to=test_phone,
                    from_=twilio_config["phone_number"]
                )

                st.success(f"✅ Call initiated to {test_phone}!")
                st.info(f"📞 Call SID: {call.sid}")

            except Exception as e:
                st.error(f"❌ Failed to make call: {e}")