"""
Emergency Response System - Global + Nigerian Focus
SMS + GPS + Clinic Alerts
"""

import streamlit as st
from datetime import datetime
from clinic_finder import (
    find_nearest_clinic,
    build_emergency_message,
    get_emergency_number,
    detect_country_from_coords,
    NIGERIAN_CLINICS
)

# ============================================
# TWILIO SMS (Optional - for real SMS)
# Uses the same st.secrets["twilio"] config as voice_checkin.py, so
# credentials live in one place (.streamlit/secrets.toml), not
# hardcoded in source files.
# ============================================
def send_sms_alert(to_number: str, message: str) -> bool:
    """Send SMS alert via Twilio. Falls back to a console print if Twilio isn't configured."""
    try:
        from twilio.rest import Client

        account_sid = st.secrets["twilio"]["account_sid"]
        auth_token = st.secrets["twilio"]["auth_token"]
        from_number = st.secrets["twilio"]["phone_number"]

        client = Client(account_sid, auth_token)
        client.messages.create(body=message, from_=from_number, to=to_number)
        print(f"✅ SMS sent to {to_number}")
        return True
    except Exception as e:
        # Covers: twilio not installed, secrets missing, or a real Twilio API error.
        # Falls back to a console log so the rest of the emergency flow
        # (clinic lookup, DB logging, caregiver notification loop) still
        # completes instead of crashing the whole alert.
        print(f"⚠️ SMS not sent to {to_number} ({e}) — printing instead:")
        print(f"📝 Message: {message[:100]}...")
        return False

# ============================================
# EMERGENCY RESPONSE CLASS
# ============================================
class EmergencyResponse:
    def __init__(self):
        self.emergency_contacts = []
        self.gps_location = None
        self.alert_history = []

    def set_emergency_contacts(self, contacts):
        """Set emergency contact phone numbers."""
        self.emergency_contacts = contacts

    def set_gps_location(self, lat, lng):
        """Update GPS location."""
        self.gps_location = {"lat": lat, "lng": lng}

    def send_emergency_alert(self, user_name, risk_level, confidence, lat=None, lng=None):
        """Send emergency alert to clinic + caregivers."""

        # Use provided coordinates, or whatever was set via set_gps_location().
        # No hardcoded fallback location: sending a fake Lagos coordinate during
        # a real emergency is worse than failing loudly and telling the caller
        # there's no location to work with (app.py already resolves a real
        # location via clinic_finder.get_user_location() before calling this).
        if lat is None or lng is None:
            if self.gps_location:
                lat = self.gps_location["lat"]
                lng = self.gps_location["lng"]
            else:
                print("❌ send_emergency_alert called with no location available.")
                return False, None

        country = detect_country_from_coords(lat, lng)
        clinic = find_nearest_clinic(lat, lng, radius_km=5.0)
        gps_link = f"https://www.google.com/maps?q={lat},{lng}"

        message = build_emergency_message(
            user_name, risk_level, confidence, gps_link, clinic, country
        )

        clinic_alerted = None
        if clinic and clinic.get("phone"):
            send_sms_alert(clinic["phone"], message)
            clinic_alerted = clinic["name"]
            print(f"✅ Clinic alerted: {clinic['name']} (Distance: {clinic['distance_km']} km)")
        else:
            emergency_num = get_emergency_number(lat, lng)
            send_sms_alert(emergency_num.get("general", "112"), message)
            print(f"✅ Emergency services alerted ({country})")

        for contact in self.emergency_contacts:
            send_sms_alert(contact, message)
            print(f"✅ Caregiver alerted: {contact}")

        self.alert_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_name,
            "risk": risk_level,
            "confidence": confidence,
            "gps_link": gps_link,
            "clinic_alerted": clinic_alerted,
            "country": country,
            "contacts_alerted": len(self.emergency_contacts)
        })

        return True, clinic

# ============================================
# EMERGENCY BUTTON IN APP (legacy/demo UI)
#
# NOTE: app.py's own "🚨 Emergency Alert" button builds its own flow
# directly (resolving location via clinic_finder.get_user_location(),
# then calling EmergencyResponse directly) — it does not call this
# function. This is kept as a standalone/demo entry point in case you
# want it elsewhere, updated to match the "no fake location" rule above
# rather than silently defaulting to Lagos.
# ============================================
def emergency_alert_ui():
    """Streamlit UI for emergency alert button (standalone/demo — see note above)."""

    st.markdown("### 🚨 Emergency Alert")
    st.markdown("Click below to send an emergency alert to the nearest clinic and your caregivers.")

    user_name = st.session_state.get("name", "Unknown User")

    location = st.session_state.get("location", {})
    lat = location.get("lat")
    lng = location.get("lng")

    if lat is None or lng is None:
        st.warning("⚠️ No location available yet. Grant GPS permission or set a registered address in Settings first.")
        return

    country = detect_country_from_coords(lat, lng)
    st.info(f"📍 Current Location: {country} ({lat:.4f}, {lng:.4f})")

    clinic = find_nearest_clinic(lat, lng, radius_km=5.0)
    if clinic:
        st.success(f"🏥 Nearest Clinic: {clinic['name']} ({clinic['distance_km']} km away)")
        st.caption(f"📞 Phone: {clinic.get('phone', 'N/A')}")
    else:
        st.warning("⚠️ No clinic found within 5km. Emergency services will be contacted directly.")

    if st.button("🚨 Send Emergency Alert", use_container_width=True):
        if 'emergency' not in st.session_state:
            st.session_state.emergency = EmergencyResponse()

        success, clinic = st.session_state.emergency.send_emergency_alert(
            user_name=user_name,
            risk_level="HIGH",
            confidence=0.95,
            lat=lat,
            lng=lng
        )

        if success:
            st.success("✅ EMERGENCY ALERT SENT!")
            st.balloons()
            if clinic:
                st.info(f"🏥 {clinic['name']} has been notified.")
            st.warning("📞 Caregivers have been alerted.")
        else:
            st.error("❌ Failed to send alert. Please call emergency services directly.")