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
    """Register a new user"""
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
        return True, "Account created successfully! Please login."
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            return False, "Email already registered. Please login."
        elif "WEAK_PASSWORD" in error_msg:
            return False, "Password must be at least 6 characters."
        else:
            return False, f"Error: {error_msg}"

def sign_in(email, password):
    """Login existing user"""
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
        
        user_info = {
            "localId": user_id,
            "email": email,
            "role": role
        }
        
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
    except:
        return {}

def update_user_data(user_id, data):
    try:
        data["last_updated"] = str(datetime.now())
        db.child("users").child(user_id).update(data)
        return True
    except:
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
    except:
        return False

def get_user_alerts(user_id, limit=20):
    try:
        alerts = db.child("alerts").child(user_id).order_by_key().limit_to_last(limit).get()
        if alerts:
            return [{"id": key, **val} for key, val in alerts.items()]
        return []
    except:
        return []

def get_all_users():
    try:
        users = db.child("users").get().val()
        if users:
            return users
        return {}
    except:
        return {}

# ============================================
# CAREGIVER FUNCTIONS
# ============================================

def link_caregiver_to_user(caregiver_email, user_email):
    """Link a caregiver to a user by email"""
    try:
        users = db.child("users").order_by_child("email").equal_to(user_email).get()
        if not users or not users.val():
            return False, "User not found. Please check the email."
        
        caregivers = db.child("users").order_by_child("email").equal_to(caregiver_email).get()
        if not caregivers or not caregivers.val():
            return False, "Caregiver account not found. Ask them to sign up first."
        
        caregiver_id = None
        for cuid, cdata in caregivers.val().items():
            caregiver_id = cuid
        
        user_id = None
        for uid, udata in users.val().items():
            user_id = uid
        
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
        
        return True, f"✅ {caregiver_email} is now your caregiver!"
        
    except Exception as e:
        return False, f"Error: {e}"

def get_user_caregivers(user_id):
    try:
        data = db.child("users").child(user_id).get().val()
        if data:
            return data.get("caregivers", [])
        return []
    except:
        return []

def get_caregiver_users(caregiver_id):
    try:
        data = db.child("users").child(caregiver_id).get().val()
        if data:
            return data.get("linked_users", [])
        return []
    except:
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
    except:
        return False

def logout():
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.name = None
    st.session_state.user_id = None
    st.session_state.logged_in = False