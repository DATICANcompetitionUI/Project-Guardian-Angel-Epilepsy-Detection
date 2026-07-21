"""
Caregiver Dashboard - Monitor loved ones' health
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from auth import db, get_user_data, get_user_alerts

def caregiver_dashboard():
    st.markdown("### 👨‍👩‍👧 Caregiver Dashboard")
    st.markdown("---")
    
    # Get caregiver's linked users
    caregiver_id = st.session_state.user_id
    
    # Get linked users from database
    try:
        caregiver_data = db.child("users").child(caregiver_id).get().val()
        if caregiver_data:
            linked_users = caregiver_data.get("linked_users", [])
        else:
            linked_users = []
    except Exception as e:
        st.error(f"Error loading caregiver data")
        linked_users = []
    
    if not linked_users:
        st.info("💡 You're not monitoring anyone yet. Ask them to add you as a caregiver.")
        return
    
    # ============================================
    # METRICS - Across all linked users
    # ============================================
    total_alerts = 0
    high_risk_users = 0
    active_monitoring = 0
    
    user_details = []
    for user_id in linked_users:
        try:
            user_data = db.child("users").child(user_id).get().val()
            if user_data:
                if user_data.get("risk_level") == "High":
                    high_risk_users += 1
                if user_data.get("monitoring_active", True):
                    active_monitoring += 1
                alerts = get_user_alerts(user_id)
                total_alerts += len(alerts)
                
                user_details.append({
                    "name": user_data.get("name", "Unknown"),
                    "email": user_data.get("email", "No email"),
                    "risk": user_data.get("risk_level", "Unknown"),
                    "monitoring": "🟢 Active" if user_data.get("monitoring_active", True) else "🔴 Paused",
                    "alerts": len(alerts)
                })
        except Exception as e:
            print(f"Error fetching user {user_id}: {e}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👤 People I Care For", len(linked_users))
    with col2:
        st.metric("⚡ High Risk", high_risk_users)
    with col3:
        st.metric("📱 Active Monitoring", active_monitoring)
    with col4:
        st.metric("🚨 Total Alerts", total_alerts)
    
    st.markdown("---")
    
    # ============================================
    # PEOPLE I CARE FOR TABLE
    # ============================================
    st.subheader("👤 People I Care For")
    
    if user_details:
        df = pd.DataFrame(user_details)
        st.dataframe(df[["name", "email", "risk", "monitoring", "alerts"]], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("No user data found.")
    
    st.markdown("---")
    
    # ============================================
    # RECENT ALERTS ACROSS ALL USERS
    # ============================================
    st.subheader("🚨 Recent Alerts")
    
    all_alerts = []
    for user_id in linked_users:
        user_data = get_user_data(user_id)
        user_name = user_data.get("name", "Unknown") if user_data else "Unknown"
        alerts = get_user_alerts(user_id, limit=10)
        
        for alert in alerts:
            all_alerts.append({
                "time": alert.get("timestamp", ""),
                "user": user_name,
                "risk": alert.get("risk", "Unknown"),
                "confidence": f"{alert.get('confidence', 0)*100:.1f}%",
                "location": alert.get("location", "N/A")[:30]
            })
    
    if all_alerts:
        df_alerts = pd.DataFrame(all_alerts).sort_values("time", ascending=False).head(20)
        st.dataframe(df_alerts, use_container_width=True, hide_index=True)
    else:
        st.info("✅ No alerts recorded yet.")
    
    # ============================================
    # CARE ACTIONS
    # ============================================
    st.markdown("---")
    st.subheader("⚡ Care Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Emergency Services (112)", use_container_width=True):
            st.warning("📞 Calling 112... Please check on your loved one.")
    
    with col2:
        if st.button("📍 View Location", use_container_width=True):
            st.info("📍 Location sharing would open here.")
    
    with col3:
        if st.button("📱 Notify User", use_container_width=True):
            st.success("📱 Notification sent to user.")