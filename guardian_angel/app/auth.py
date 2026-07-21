"""
Firebase Authentication - Complete Auth System with Caregiver Support
"""

import pyrebase
import streamlit as st
from datetime import datetime
from firebase_config import FIREBASE_CONFIG

# Initialize Firebase
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()

# ============================================
# AUTHENTICATION FUNCTIONS
# ============================================

def sign_up(email, password, role="user", name="User"):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        user_id = user.get('localId')
        db.child("users").child(user_id).set({
            "email": email,
            "name": name,
            "role": role,
            "created_at": str(datetime.now()),
            "risk_level": "Low",
            "monitoring_active": True,
            "contacts": [],
            "caregivers": [],
            "linked_users": [],
            "alert_history": [],
            "last_updated": str(datetime.now())
        })
        return True, "Account created successfully!"
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            return False, "Email already registered."
        elif "WEAK_PASSWORD" in error_msg:
            return False, "Password must be at least 6 characters."
        else:
            return False, f"Error: {error_msg}"

def sign_in(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_id = user.get('localId')
        user_data = db.child("users").child(user_id).get().val()
        if user_data:
            role = user_data.get("role", "user")
            name = user_data.get("name", "User")
        else:
            role = "user"
            name = "User"
            db.child("users").child(user_id).set({
                "email": email,
                "name": name,
                "role": role,
                "created_at": str(datetime.now()),
                "risk_level": "Low",
                "monitoring_active": True,
                "contacts": [],
                "caregivers": [],
                "linked_users": [],
                "alert_history": [],
                "last_updated": str(datetime.now())
            })
        user_info = {"localId": user_id, "email": email, "role": role}
        return True, user_info, role, name
    except Exception as e:
        error_msg = str(e)
        if "INVALID_EMAIL" in error_msg:
            return False, "Invalid email format.", None, None
        elif "INVALID_PASSWORD" in error_msg:
            return False, "Incorrect password.", None, None
        elif "EMAIL_NOT_FOUND" in error_msg:
            return False, "Email not registered. Please sign up.", None, None
        else:
            return False, f"Login failed: {error_msg}", None, None

def get_user_data(user_id):
    try:
        user_data = db.child("users").child(user_id).get().val()
        return user_data if user_data else {}
    except Exception:
        return {}

def update_user_data(user_id, data):
    try:
        data["last_updated"] = str(datetime.now())
        db.child("users").child(user_id).update(data)
        return True
    except Exception:
        return False

def save_alert(user_id, alert_data):
    try:
        db.child("alerts").child(user_id).push({
            "timestamp": str(datetime.now()),
            "risk": alert_data.get("risk", "HIGH"),
            "confidence": alert_data.get("confidence", 0.0),
            "location": alert_data.get("location", "N/A"),
            "country": alert_data.get("country", "Unknown"),
            "clinic_alerted": alert_data.get("clinic_alerted", "None"),
            "resolved": alert_data.get("resolved", False)
        })
        return True
    except Exception:
        return False

def get_user_alerts(user_id, limit=20):
    try:
        alerts = db.child("alerts").child(user_id).order_by_key().limit_to_last(limit).get()
        if alerts:
            return [{"id": key, **val} for key, val in alerts.items()]
        return []
    except Exception:
        return []

def get_all_users():
    try:
        users = db.child("users").get().val()
        if users:
            return users
        return {}
    except Exception:
        return {}

# ============================================
# CAREGIVER FUNCTIONS
# ============================================

def link_caregiver_to_user(caregiver_email, user_email):
    """Link a caregiver to a user by email"""
    try:
        users_data = db.child("users").get().val()
        if not users_data:
            return False, "No users found."

        user_id = None
        user_name = None
        for uid, udata in users_data.items():
            if isinstance(udata, dict) and udata.get("email") == user_email:
                user_id = uid
                user_name = udata.get("name", "User")
                break

        if not user_id:
            return False, "User not found. Please check the email."

        caregiver_id = None
        caregiver_name = None
        for uid, udata in users_data.items():
            if isinstance(udata, dict) and udata.get("email") == caregiver_email:
                caregiver_id = uid
                caregiver_name = udata.get("name", "Caregiver")
                break

        if not caregiver_id:
            return False, "Caregiver account not found. Ask them to sign up first."

        user_data = get_user_data(user_id)
        caregivers_list = user_data.get("caregivers", [])
        if caregiver_id in caregivers_list:
            return False, "This caregiver is already linked to your account."

        caregivers_list.append(caregiver_id)
        db.child("users").child(user_id).update({"caregivers": caregivers_list})

        caregiver_data = get_user_data(caregiver_id)
        linked_users = caregiver_data.get("linked_users", [])
        if user_id not in linked_users:
            linked_users.append(user_id)
            db.child("users").child(caregiver_id).update({"linked_users": linked_users})

        return True, f"✅ {caregiver_name} is now your caregiver!"

    except Exception as e:
        return False, f"Error: {e}"

def get_user_caregivers(user_id):
    """Get all caregivers linked to a user"""
    try:
        data = db.child("users").child(user_id).get().val()
        if data:
            return data.get("caregivers", [])
        return []
    except Exception:
        return []

def get_caregiver_users(caregiver_id):
    """Get all users linked to a caregiver"""
    try:
        data = db.child("users").child(caregiver_id).get().val()
        if data:
            return data.get("linked_users", [])
        return []
    except Exception:
        return []

def add_caregiver_by_phone(user_id, caregiver_phone):
    try:
        user_data = db.child("users").child(user_id).get().val()
        if user_data:
            caregivers = user_data.get("caregivers", [])
            if caregiver_phone not in caregivers:
                caregivers.append(caregiver_phone)
                db.child("users").child(user_id).update({"caregivers": caregivers})
                caregiver_data = db.child("users").order_by_child("phone").equal_to(caregiver_phone).get()
                if caregiver_data:
                    for cuid, cdata in caregiver_data.val().items():
                        linked_users = cdata.get("linked_users", [])
                        if user_id not in linked_users:
                            linked_users.append(user_id)
                            db.child("users").child(cuid).update({"linked_users": linked_users})
        return True
    except Exception:
        return False

# ============================================
# RISK NOTIFICATION FUNCTIONS
# Preventive warning sent when risk_level goes HIGH — distinct from
# save_alert(), which logs an actual detected/confirmed seizure event.
# ============================================

def send_risk_notification(user_id, risk_level):
    """Send a warning notification (SMS + DB log) when risk level goes HIGH."""
    try:
        user_data = get_user_data(user_id)
        user_name = user_data.get("name", "User")
        caregivers = user_data.get("caregivers", [])

        message = (
            "⚠️ GUARDIAN ANGEL - HIGH RISK ALERT\n"
            f"User: {user_name}\n"
            f"Risk Level: HIGH\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "Please check on the user. Risk of seizure is elevated.\n"
            "This is a WARNING — not an emergency alert."
        )

        # send_sms_alert lives in emergency_response.py (Twilio-backed,
        # falls back to a console log if Twilio secrets aren't configured).
        try:
            from emergency_response import send_sms_alert
        except ImportError as e:
            print(f"Could not import send_sms_alert: {e}")
            send_sms_alert = None

        user_phone = user_data.get("phone")
        if user_phone and send_sms_alert:
            try:
                send_sms_alert(user_phone, message)
            except Exception as e:
                print(f"Error sending SMS to user {user_id}: {e}")

        for caregiver_id in caregivers:
            caregiver_data = get_user_data(caregiver_id)
            if caregiver_data:
                caregiver_phone = caregiver_data.get("phone")
                if caregiver_phone and send_sms_alert:
                    try:
                        send_sms_alert(caregiver_phone, message)
                    except Exception as e:
                        print(f"Error sending SMS to caregiver {caregiver_id}: {e}")

        db.child("risk_notifications").child(user_id).push({
            "timestamp": str(datetime.now()),
            "risk_level": risk_level,
            "message": message,
            "sent_to": caregivers + [user_id],
            "sms_sent": bool(send_sms_alert)
        })

        return True
    except Exception as e:
        print(f"Error sending risk notification: {e}")
        return False

# ============================================
# LOGOUT FUNCTION
# ============================================

def logout():
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.name = None
    st.session_state.user_id = None
    st.session_state.logged_in = False