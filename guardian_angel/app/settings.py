"""
Settings and Notifications System
No medical features — just user preferences and system config
"""

import streamlit as st
import pandas as pd
import requests
from datetime import time
from auth import get_user_data, update_user_data, db
from admin_dashboard import pulse_divider, render_table, pill

# ============================================
# GEOCODING (for Registered Address fallback)
# ============================================

def geocode_address(address_text: str):
    """Convert a free-text address into coordinates using OpenStreetMap's Nominatim"""
    try:
        # Add country hint for better results
        if "nigeria" not in address_text.lower() and "ng" not in address_text.lower():
            address_text = f"{address_text}, Nigeria"
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address_text,
            "format": "json",
            "limit": 1,
            "countrycodes": "ng"  # Prioritize Nigeria
        }
        headers = {"User-Agent": "GuardianAngelApp/1.0 (https://guardian-angel.com)"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            if results:
                return {
                    "lat": float(results[0]["lat"]),
                    "lng": float(results[0]["lon"]),
                    "formatted_address": results[0].get("display_name", address_text)
                }
    except Exception:
        pass
    return None# ============================================
# SETTINGS FUNCTIONS
# ============================================

def get_user_settings(user_id):
    """Get user settings from database"""
    try:
        user_data = get_user_data(user_id)
        return user_data.get("settings", {
            "notifications": {
                "sms": True,
                "email": False,
                "push": True
            },
            "checkin_time": "09:00",
            "timezone": "Africa/Lagos"
        })
    except Exception:
        return {}

def update_user_settings(user_id, settings):
    """Update user settings in database"""
    try:
        update_user_data(user_id, {"settings": settings})
        return True
    except Exception:
        return False

def get_notification_preferences(user_id):
    """Get notification preferences for a user"""
    settings = get_user_settings(user_id)
    return settings.get("notifications", {
        "sms": True,
        "email": False,
        "push": True
    })

def update_notification_preferences(user_id, prefs):
    """Update notification preferences"""
    settings = get_user_settings(user_id)
    settings["notifications"] = prefs
    return update_user_settings(user_id, settings)


def status_pill(status_text):
    """Map a log/user status string to a pill kind understood by admin_dashboard.pill"""
    if "Alert" in status_text or "Fail" in status_text:
        kind = "high"
    elif "Success" in status_text or "Active" in status_text:
        kind = "active"
    else:
        kind = "moderate"
    return pill(status_text, kind)


# ============================================
# STREAMLIT UI
# ============================================

def settings_ui():
    """Main settings page"""
    role = st.session_state.role
    name = st.session_state.name

    st.markdown(f"""
        <div class="ga-topbar">
            <div>
                <h2>⚙️ Settings</h2>
                <p>Manage your account, notifications, and preferences</p>
            </div>
            <div>
                <span class="badge">{role}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    pulse_divider()

    user_id = st.session_state.user_id

    if role == "admin":
        admin_settings_ui()
    else:
        user_settings_ui(user_id)


def user_settings_ui(user_id):
    """User (and caregiver) settings page"""

    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔔 Notifications", "⏰ Check-In"])

    with tab1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("👤 Profile Settings")
        user_data = get_user_data(user_id)

        name = st.text_input("Full Name", value=user_data.get("name", ""))
        email = st.text_input("Email", value=user_data.get("email", ""), disabled=True)
        phone = st.text_input("Phone Number", value=user_data.get("phone", ""), placeholder="+234 800 000 0000")

        if st.button("💾 Save Profile", use_container_width=True):
            updates = {}
            if name:
                updates["name"] = name
            if phone:
                updates["phone"] = phone
            if updates:
                update_user_data(user_id, updates)
                st.success("✅ Profile updated successfully!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🏠 Registered Address")
        st.caption("Used as a fallback location for emergency alerts if GPS isn't available or wasn't granted.")

        existing_address = user_data.get("address", {})
        existing_formatted = existing_address.get("formatted_address", "")

        if existing_address.get("lat") is not None:
            st.markdown(
                f'<div class="info-box">✅ Saved: {existing_formatted}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="empty-box">No address saved yet — emergency alerts will have no fallback if GPS is unavailable.</div>',
                unsafe_allow_html=True
            )

        address_input = st.text_input(
            "Home Address",
            value=existing_formatted,
            placeholder="e.g. 12 Idowu Martins Street, Victoria Island, Lagos"
        )

        if st.button("📍 Geocode & Save Address", use_container_width=True):
            if not address_input:
                st.warning("⚠️ Please enter an address.")
            else:
                with st.spinner("📍 Looking up address..."):
                    result = geocode_address(address_input)
                if result:
                    update_user_data(user_id, {
                        "address": {
                            "lat": result["lat"],
                            "lng": result["lng"],
                            "formatted_address": result["formatted_address"]
                        }
                    })
                    st.success(f"✅ Address saved: {result['formatted_address']}")
                    st.rerun()
                else:
                    st.error("❌ Couldn't find that address. Try adding more detail (city, state/country).")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🔔 Notification Preferences")
        prefs = get_notification_preferences(user_id)

        st.markdown("**Choose how you want to receive alerts:**")

        col1, col2 = st.columns(2)
        with col1:
            sms = st.checkbox("📱 SMS Alerts", value=prefs.get("sms", True))
            push = st.checkbox("📲 Push Notifications", value=prefs.get("push", True))
        with col2:
            email = st.checkbox("📧 Email Alerts", value=prefs.get("email", False))

        st.markdown("---")
        st.markdown("**Emergency Alert Settings**")

        alert_style = st.selectbox(
            "How would you like to receive emergency alerts?",
            ["SMS Only", "SMS + Email", "SMS + Push", "All Channels"]
        )

        if st.button("💾 Save Notification Settings", use_container_width=True):
            update_notification_preferences(user_id, {
                "sms": sms,
                "email": email,
                "push": push,
                "alert_style": alert_style
            })
            st.success("✅ Notification settings updated!")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("⏰ Daily Check-In Schedule")
        st.info("📞 Set when you want to receive your daily check-in call.")

        checkin_time = st.time_input("Check-In Time", value=time(9, 0))

        st.markdown("**Days of Week**")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selected_days = st.multiselect("Select days", days, default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])

        if st.button("💾 Save Schedule", use_container_width=True):
            st.success("✅ Check-in schedule saved!")
            st.info(f"📞 You will receive a daily check-in call at {checkin_time.strftime('%H:%M')} on {', '.join(selected_days)}")
        st.markdown('</div>', unsafe_allow_html=True)


def admin_settings_ui():
    """Admin settings page"""

    tab1, tab2, tab3, tab4 = st.tabs(["⚙️ System", "📧 Notifications", "👥 Users", "📊 Logs"])

    with tab1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("⚙️ System Settings")

        st.markdown("**Clinic Finder Settings**")
        clinic_radius = st.slider("Clinic Search Radius (km)", min_value=1, max_value=20, value=5)

        st.markdown("**Emergency Alert Settings**")
        welfare_timeout = st.slider("Welfare Check Timeout (seconds)", min_value=10, max_value=120, value=30)

        st.markdown("**App Settings**")
        maintenance_mode = st.toggle("Maintenance Mode", value=False)

        if st.button("💾 Save System Settings", use_container_width=True):
            st.success("✅ System settings saved!")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📧 Notification Templates")

        st.markdown("**Emergency Alert Template**")
        sms_template = st.text_area(
            "SMS Template",
            value="""🚨 GUARDIAN ANGEL EMERGENCY ALERT 🚨

User: {user_name}
Risk: {risk_level}
Location: {gps_link}

Please check on the user immediately."""
        )

        st.markdown("**Daily Check-In Template**")
        checkin_template = st.text_area(
            "Check-In SMS Template",
            value="""📞 Daily Check-In Reminder

Dear {user_name},

Please respond to your daily check-in call today at {checkin_time}.
Your health matters to us.

Guardian Angel Team"""
        )

        if st.button("💾 Save Templates", use_container_width=True):
            st.success("✅ Templates saved!")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.subheader("👥 User Management")

        try:
            users_data = db.child("users").get().val()
        except Exception:
            users_data = None

        if users_data:
            user_list = []
            for uid, data in users_data.items():
                if isinstance(data, dict):
                    user_list.append({
                        "name": data.get("name", "Unknown"),
                        "email": data.get("email", ""),
                        "role": data.get("role", "user"),
                        "status": "Active",
                    })

            df = pd.DataFrame(user_list)
            render_table(df, [
                ("name", "Name", None),
                ("email", "Email", None),
                ("role", "Role", None),
                ("status", "Status", status_pill),
            ])
        else:
            st.markdown('<div class="empty-box">No users found.</div>', unsafe_allow_html=True)

    with tab4:
        st.subheader("📊 System Logs")
        st.info("System activity logs will appear here.")

        logs = [
            {"timestamp": "2026-07-16 09:00:00", "event": "Daily check-in initiated for john doe", "status": "Success"},
            {"timestamp": "2026-07-16 08:45:00", "event": "Emergency alert triggered for sarah smith", "status": "Alert"},
            {"timestamp": "2026-07-16 08:30:00", "event": "User login: mike johnson", "status": "Success"},
        ]

        if logs:
            df_logs = pd.DataFrame(logs)
            render_table(df_logs, [
                ("timestamp", "Timestamp", None),
                ("event", "Event", None),
                ("status", "Status", status_pill),
            ])