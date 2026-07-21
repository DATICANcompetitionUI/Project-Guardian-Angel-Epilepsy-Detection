"""
Admin Dashboard - View all users, alerts, and clinic usage
Professional redesign with custom styling
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from auth import db


# ============================================
# STYLING
# ============================================
def inject_css():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --ga-primary: #1F6F5C;
            --ga-primary-dark: #164F41;
            --ga-primary-light: #E4F1EC;
            --ga-alert: #D9583A;
            --ga-alert-bg: #FBEAE5;
            --ga-warn: #C68A2E;
            --ga-warn-bg: #FBF2E1;
            --ga-success: #2F9E64;
            --ga-success-bg: #E9F7EE;
        }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        h1, h2, h3, h4 { font-family: 'Manrope', sans-serif; }

        /* ---------- General ---------- */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        #MainMenu, footer {visibility: hidden;}

        /* ---------- Header ---------- */
        .ga-header {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 22px 28px;
            border-radius: 16px;
            background: linear-gradient(135deg, #1F6F5C 0%, #164F41 100%);
            margin-bottom: 8px;
            box-shadow: 0 4px 16px rgba(31, 111, 92, 0.20);
        }
        .ga-header .icon {
            font-size: 32px;
            background: rgba(255,255,255,0.15);
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
        }
        .ga-header h1 {
            color: #fff;
            font-size: 22px;
            font-weight: 700;
            margin: 0;
        }
        .ga-header p {
            color: rgba(255,255,255,0.75);
            font-size: 13px;
            margin: 2px 0 0 0;
        }

        /* ---------- Metric cards ---------- */
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 14px;
            margin-bottom: 26px;
        }
        @media (max-width: 900px) {
            .metric-grid { grid-template-columns: repeat(2, 1fr); }
        }
        .metric-card {
            background: #ffffff;
            border: 1px solid #e8ecf1;
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            transition: box-shadow 0.15s ease;
        }
        .metric-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .metric-card .label {
            font-size: 12px;
            font-weight: 600;
            color: #6b7684;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;
        }
        .metric-card .value {
            font-size: 28px;
            font-weight: 700;
            color: #1a2433;
            line-height: 1;
        }
        .metric-card.alert .value { color: var(--ga-alert); }
        .metric-card.good .value { color: var(--ga-success); }

        /* ---------- Section headers ---------- */
        .section-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 700;
            color: #1a2433;
            margin: 30px 0 14px 0;
        }
        .section-title .badge-count {
            background: #eef2f7;
            color: #4a5568;
            font-size: 12px;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 20px;
        }

        /* ---------- Styled table ---------- */
        .ga-table-wrap {
            background: #fff;
            border: 1px solid #e8ecf1;
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        table.ga-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
        }
        table.ga-table thead th {
            background: #f7f9fb;
            text-align: left;
            padding: 12px 16px;
            font-weight: 600;
            color: #5a6472;
            font-size: 11.5px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            border-bottom: 1px solid #e8ecf1;
        }
        table.ga-table tbody td {
            padding: 11px 16px;
            border-bottom: 1px solid #f0f3f6;
            color: #2d3746;
            vertical-align: middle;
        }
        table.ga-table tbody tr:last-child td { border-bottom: none; }
        table.ga-table tbody tr:hover { background: #fafbfc; }

        /* ---------- Badges ---------- */
        .pill {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11.5px;
            font-weight: 600;
            white-space: nowrap;
        }
        .pill-admin { background: var(--ga-primary-light); color: var(--ga-primary-dark); }
        .pill-user { background: var(--ga-success-bg); color: #1f7a44; }
        .pill-caregiver { background: var(--ga-warn-bg); color: var(--ga-warn); }
        .pill-low { background: var(--ga-success-bg); color: var(--ga-success); }
        .pill-moderate { background: var(--ga-warn-bg); color: var(--ga-warn); }
        .pill-high { background: var(--ga-alert-bg); color: var(--ga-alert); }
        .pill-active { background: var(--ga-success-bg); color: var(--ga-success); }
        .pill-paused { background: var(--ga-alert-bg); color: var(--ga-alert); }
        .dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
        .dot-green { background: var(--ga-success); }
        .dot-red { background: var(--ga-alert); }

        /* ---------- Info / empty state boxes ---------- */
        .info-box {
            background: var(--ga-primary-light);
            border: 1px solid #d3e6df;
            border-radius: 12px;
            padding: 14px 18px;
            color: var(--ga-primary-dark);
            font-size: 13.5px;
            margin: 10px 0 20px 0;
        }
        .empty-box {
            background: #f7f9fb;
            border: 1px dashed #d7dde5;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
            color: #8a94a3;
            font-size: 13.5px;
            margin: 10px 0 20px 0;
        }
        .success-box {
            background: var(--ga-success-bg);
            border: 1px solid #cdeeda;
            border-radius: 12px;
            padding: 14px 18px;
            color: #1f7a44;
            font-size: 13.5px;
            margin: 10px 0 20px 0;
        }

        /* ---------- Buttons ---------- */
        div.stButton > button {
            border-radius: 10px;
            border: none;
            font-weight: 600;
            padding: 0.5rem 1rem;
            background: var(--ga-primary);
            color: #fff;
        }
        div.stButton > button:hover {
            background: var(--ga-primary-dark);
            color: #fff;
        }

        /* ---------- Signature: pulse / EKG divider ---------- */
        .pulse-divider { width: 100%; height: 30px; margin: 4px 0 22px 0; }
        .pulse-divider svg { width: 100%; height: 100%; display: block; }

        .footer-note {
            text-align: center;
            color: #93A399;
            font-size: 12px;
            margin-top: 40px;
        }
    </style>
    """, unsafe_allow_html=True)


def pulse_divider(color="#1F6F5C", opacity="0.5"):
    """Signature EKG pulse-line motif, shared with app.py, used as a divider."""
    st.markdown(f"""
    <div class="pulse-divider">
        <svg viewBox="0 0 600 30" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="0,15 140,15 165,15 178,3 190,27 203,15 230,15 600,15"
                fill="none" stroke="{color}" stroke-opacity="{opacity}" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)


def pill(text, kind):
    return f'<span class="pill pill-{kind}">{text}</span>'


def role_pill(role):
    kind = {"admin": "admin", "user": "user", "caregiver": "caregiver"}.get(role, "user")
    return pill(role.capitalize(), kind)


def risk_pill(risk):
    kind = {"Low": "low", "Moderate": "moderate", "High": "high"}.get(risk, "low")
    return pill(risk, kind)


def quality_pill(value):
    """For self-reported Sleep/Energy values — reuses the low/moderate/high palette
    so 'Good' reads green, 'OK' reads amber, 'Poor'/'Low' reads red, consistent
    with the Risk column's coloring."""
    kind = {"Good": "low", "OK": "moderate", "Poor": "high", "Low": "high"}.get(value, "moderate")
    return pill(value, kind)


def monitoring_pill(is_active_str):
    if "Active" in is_active_str:
        return f'<span class="dot dot-green"></span><span class="pill pill-active">Active</span>'
    return f'<span class="dot dot-red"></span><span class="pill pill-paused">Paused</span>'


def render_table(df, columns_map):
    """columns_map: list of (df_col, header_label, formatter_fn or None)"""
    thead = "".join(f"<th>{label}</th>" for _, label, _ in columns_map)
    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col, _, fmt in columns_map:
            val = row[col]
            cells += f"<td>{fmt(val) if fmt else val}</td>"
        rows_html += f"<tr>{cells}</tr>"
    html = f"""
    <div class="ga-table-wrap">
      <table class="ga-table">
        <thead><tr>{thead}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def metric_card(label, value, icon="", kind=""):
    cls = f"metric-card {kind}".strip()
    return f'<div class="{cls}"><div class="label">{icon} {label}</div><div class="value">{value}</div></div>'


# ============================================
# MAIN
# ============================================
def admin_dashboard():
    inject_css()

    st.markdown("""
    <div class="ga-header">
        <div class="icon">🩺</div>
        <div>
            <h1>Admin Dashboard</h1>
            <p>Guardian Angel — AI Seizure Detection System</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    pulse_divider()

    try:
        # Get all users
        users_data = db.child("users").get()

        if not users_data or not users_data.val():
            st.markdown('<div class="empty-box">No users registered yet.</div>', unsafe_allow_html=True)
            return

        users_dict = users_data.val()

        # Prepare user list with clinic info
        user_list = []
        high_risk_count = 0
        active_monitoring_count = 0
        admin_count = 0
        users_with_clinics = 0

        for user_id, data in users_dict.items():
            if isinstance(data, dict):
                risk = data.get("risk_level", "Unknown")
                monitoring = data.get("monitoring_active", True)
                role = data.get("role", "user")

                if risk == "High":
                    high_risk_count += 1
                if monitoring:
                    active_monitoring_count += 1
                if role == "admin":
                    admin_count += 1

                clinic_name = "None"
                last_alert_time = "N/A"

                try:
                    alerts = db.child("alerts").child(user_id).limit_to_last(1).get()
                    if alerts and alerts.val():
                        for alert_id, alert in alerts.val().items():
                            if isinstance(alert, dict):
                                clinic_name = alert.get("clinic_alerted", "None")
                                if clinic_name != "None" and clinic_name != "User requested help":
                                    users_with_clinics += 1
                                last_alert_time = alert.get("timestamp", "N/A")
                except Exception:
                    pass

                contacts = data.get("contacts", [])
                contacts_str = ", ".join(contacts) if contacts else "None"

                user_list.append({
                    "id": user_id[:8],
                    "name": data.get("name", "Unknown"),
                    "email": data.get("email", "No email"),
                    "role": role,
                    "risk": risk,
                    "monitoring": "🟢 Active" if monitoring else "🔴 Paused",
                    "contacts": contacts_str,
                    "contacts_count": len(contacts),
                    "clinic": clinic_name,
                    "last_alert": last_alert_time[:16] if last_alert_time != "N/A" else "N/A",
                    "joined": data.get("created_at", "").split(" ")[0] if data.get("created_at") else "N/A"
                })

        # ============================================
        # METRICS
        # ============================================
        total_alerts = 0
        try:
            for user_id in users_dict.keys():
                alerts = db.child("alerts").child(user_id).get()
                if alerts and alerts.val():
                    total_alerts += len(alerts.val())
        except Exception:
            pass

        metrics_html = '<div class="metric-grid">'
        metrics_html += metric_card("Total Users", len(user_list), "👤")
        metrics_html += metric_card("Admins", admin_count, "👑")
        metrics_html += metric_card("High Risk", high_risk_count, "⚡", "alert" if high_risk_count else "")
        metrics_html += metric_card("Active Monitoring", active_monitoring_count, "📡", "good" if active_monitoring_count else "")
        metrics_html += metric_card("Total Alerts", total_alerts, "🚨", "alert" if total_alerts else "")
        metrics_html += metric_card("Clinics Used", users_with_clinics, "🏥")
        metrics_html += '</div>'
        st.markdown(metrics_html, unsafe_allow_html=True)

        # ============================================
        # USERS TABLE
        # ============================================
        st.markdown(f'<div class="section-title">👤 All Users <span class="badge-count">{len(user_list)}</span></div>', unsafe_allow_html=True)

        if user_list:
            df = pd.DataFrame(user_list)
            has_clinic_data = any(u["clinic"] != "None" for u in user_list)

            base_columns = [
                ("name", "Name", None),
                ("email", "Email", None),
                ("role", "Role", role_pill),
                ("risk", "Risk", risk_pill),
                ("monitoring", "Monitoring", monitoring_pill),
            ]
            if has_clinic_data:
                base_columns.append(("clinic", "Last Clinic Alerted", None))
                base_columns.append(("last_alert", "Alert Time", None))
            base_columns.append(("contacts", "Emergency Contacts", None))
            base_columns.append(("joined", "Joined", None))

            render_table(df, base_columns)

            if not has_clinic_data:
                st.markdown('<div class="info-box">💡 Clinic data will appear here when users trigger emergency alerts with their location.</div>', unsafe_allow_html=True)

            # ============================================
            # CLINIC USAGE SUMMARY
            # ============================================
            st.markdown('<div class="section-title">🏥 Clinic Usage Summary</div>', unsafe_allow_html=True)

            clinic_counts = {}
            for user in user_list:
                clinic = user.get("clinic", "None")
                if clinic != "None" and clinic != "User requested help":
                    clinic_name = clinic.split("(")[0].strip() if "(" in clinic else clinic
                    clinic_counts[clinic_name] = clinic_counts.get(clinic_name, 0) + 1

            if clinic_counts:
                col1, col2 = st.columns([2, 1])
                with col1:
                    clinic_df = pd.DataFrame([
                        {"Clinic": name, "Times Alerted": count}
                        for name, count in sorted(clinic_counts.items(), key=lambda x: x[1], reverse=True)
                    ])
                    render_table(clinic_df, [("Clinic", "Clinic", None), ("Times Alerted", "Times Alerted", None)])
                    st.caption(f"📊 {len(clinic_counts)} different clinics have been alerted.")
                with col2:
                    top_clinic = max(clinic_counts.items(), key=lambda x: x[1])
                    st.markdown(metric_card("Most Used Clinic", top_clinic[0], "🏥"), unsafe_allow_html=True)
                    st.caption(f"{top_clinic[1]} alerts sent")
            else:
                st.markdown('<div class="empty-box">No clinics have been alerted yet. Emergency alerts will track clinic usage.</div>', unsafe_allow_html=True)

            # ============================================
            # FILTER CONTROLS
            # ============================================
            with st.expander("🔍 Filter Users"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    filter_role = st.selectbox("Filter by Role", ["All", "admin", "user"])
                with col2:
                    filter_risk = st.selectbox("Filter by Risk", ["All", "Low", "Moderate", "High"])
                with col3:
                    filter_monitoring = st.selectbox("Filter by Monitoring", ["All", "Active", "Paused"])
                with col4:
                    clinic_options = ["All"] + list(clinic_counts.keys()) if clinic_counts else ["All"]
                    filter_clinic = st.selectbox("Filter by Clinic Alerted", clinic_options)

                filtered = df.copy()
                if filter_role != "All":
                    filtered = filtered[filtered["role"] == filter_role]
                if filter_risk != "All":
                    filtered = filtered[filtered["risk"] == filter_risk]
                if filter_monitoring != "All":
                    filtered = filtered[filtered["monitoring"].str.contains(filter_monitoring, na=False)]
                if filter_clinic != "All" and filter_clinic and has_clinic_data:
                    filtered = filtered[filtered["clinic"].str.contains(filter_clinic, na=False)]

                if not filtered.empty:
                    render_table(filtered, base_columns)
                    st.caption(f"Showing {len(filtered)} of {len(df)} users")
                else:
                    st.markdown('<div class="empty-box">No users match these filters.</div>', unsafe_allow_html=True)

            # ============================================
            # SUMMARY STATS
            # ============================================
            with st.expander("📊 User Contact Summary"):
                col1, col2 = st.columns(2)
                with col1:
                    users_with_contacts = len([u for u in user_list if u["contacts"] != "None"])
                    st.markdown(metric_card("Users with Contacts", users_with_contacts, "📇"), unsafe_allow_html=True)
                with col2:
                    total_contacts = sum([u["contacts_count"] for u in user_list])
                    st.markdown(metric_card("Total Contacts Saved", total_contacts, "📞"), unsafe_allow_html=True)

            # ============================================
            # EXPORT DATA
            # ============================================
            with st.expander("📊 Export Data"):
                export_df = df[[c for c, _, _ in base_columns]].copy()
                export_df.columns = [label for _, label, _ in base_columns]
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"guardian_angel_users_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.markdown('<div class="empty-box">No users found.</div>', unsafe_allow_html=True)

        # ============================================
        # RECENT ALERTS
        # ============================================
        st.markdown('<div class="section-title">🚨 Recent Alerts</div>', unsafe_allow_html=True)
        all_alerts = []

        try:
            for user_id in users_dict.keys():
                alerts = db.child("alerts").child(user_id).limit_to_last(10).get()
                if alerts and alerts.val():
                    user_info = users_dict.get(user_id, {})
                    user_name = user_info.get("name", "Unknown")
                    contacts = user_info.get("contacts", [])
                    contact_str = ", ".join(contacts) if contacts else "None"

                    for alert_id, alert in alerts.val().items():
                        if isinstance(alert, dict):
                            all_alerts.append({
                                "time": alert.get("timestamp", ""),
                                "user": user_name,
                                "risk": alert.get("risk", "Unknown"),
                                "confidence": f"{alert.get('confidence', 0)*100:.1f}%",
                                "clinic": alert.get("clinic_alerted", "None"),
                                "location": alert.get("location", "N/A")[:30],
                                "contact": contact_str
                            })
        except Exception:
            pass

        if all_alerts:
            df_alerts = pd.DataFrame(all_alerts).sort_values("time", ascending=False).head(20)
            has_clinic_in_alerts = any(a["clinic"] != "None" for a in all_alerts)

            if has_clinic_in_alerts:
                alert_cols = [("time", "Time", None), ("user", "User", None), ("risk", "Risk", risk_pill),
                              ("clinic", "Clinic", None), ("location", "Location", None)]
            else:
                alert_cols = [("time", "Time", None), ("user", "User", None), ("risk", "Risk", risk_pill),
                              ("location", "Location", None)]
            render_table(df_alerts, alert_cols)
        else:
            st.markdown('<div class="success-box">✅ No alerts recorded yet.</div>', unsafe_allow_html=True)

        # ============================================
        # DAILY CHECK-IN TRENDS
        # Self-reported sleep/energy/symptoms feeding the coarse risk trend
        # (see risk_trend.py) — this is the "why" behind each user's current
        # risk_level shown in the All Users table above.
        # ============================================
        st.markdown('<div class="section-title">📋 Daily Check-In Trends</div>', unsafe_allow_html=True)

        from datetime import date as _date
        today_str = _date.today().isoformat()

        checkin_rows = []
        checked_in_today = 0
        high_risk_today = 0

        for user_id, data in users_dict.items():
            if not isinstance(data, dict):
                continue
            user_name = data.get("name", "Unknown")
            try:
                history = db.child("daily_checkins").child(user_id).order_by_key().limit_to_last(5).get()
                if history and history.val():
                    for date_key, entry in sorted(history.val().items(), reverse=True):
                        if isinstance(entry, dict):
                            if date_key == today_str:
                                checked_in_today += 1
                                if entry.get("risk_level") == "High":
                                    high_risk_today += 1
                            checkin_rows.append({
                                "user": user_name,
                                "date": entry.get("date", date_key),
                                "sleep": entry.get("sleep_quality", "N/A"),
                                "energy": entry.get("energy_level", "N/A"),
                                "symptoms": "⚠️ Yes" if entry.get("symptoms_today") else "No",
                                "score": entry.get("score", 0),
                                "risk": entry.get("risk_level", "Unknown"),
                            })
            except Exception:
                pass

        checkin_metrics = '<div class="metric-grid">'
        checkin_metrics += metric_card("Checked In Today", f"{checked_in_today}/{len(user_list)}", "📋")
        checkin_metrics += metric_card("High Risk Today", high_risk_today, "⚡", "alert" if high_risk_today else "")
        checkin_metrics += '</div>'
        st.markdown(checkin_metrics, unsafe_allow_html=True)

        if checkin_rows:
            checkin_rows.sort(key=lambda r: r["date"], reverse=True)
            df_checkins = pd.DataFrame(checkin_rows[:30])
            render_table(df_checkins, [
                ("user", "User", None),
                ("date", "Date", None),
                ("sleep", "Sleep", quality_pill),
                ("energy", "Energy", quality_pill),
                ("symptoms", "Symptoms", None),
                ("score", "Score", None),
                ("risk", "Computed Risk", risk_pill),
            ])
            st.caption("Score = Sleep (0–2) + Energy (0–2) + Symptoms (0 or 3) → Low ≤1, Moderate 2–3, High ≥4. Fully rule-based, no black-box model.")
        else:
            st.markdown('<div class="empty-box">No daily check-ins submitted yet. They\'ll appear here once users start checking in.</div>', unsafe_allow_html=True)

        # ============================================
        # ADMIN QUICK ACTIONS
        # ============================================
        st.markdown('<div class="section-title">⚡ Admin Quick Actions</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Refresh Data", use_container_width=True):
                st.rerun()

        with col2:
            if st.button("📋 View All Alerts", use_container_width=True):
                if all_alerts:
                    render_table(pd.DataFrame(all_alerts), [
                        ("time", "Time", None), ("user", "User", None), ("risk", "Risk", risk_pill),
                        ("confidence", "Confidence", None), ("clinic", "Clinic", None),
                        ("location", "Location", None), ("contact", "Contact", None)
                    ])
                else:
                    st.markdown('<div class="empty-box">No alerts to view.</div>', unsafe_allow_html=True)

        with col3:
            if st.button("🏥 Clinic Stats", use_container_width=True):
                if clinic_counts:
                    render_table(
                        pd.DataFrame([{"Clinic": k, "Alerts": v} for k, v in clinic_counts.items()]),
                        [("Clinic", "Clinic", None), ("Alerts", "Alerts", None)]
                    )
                else:
                    st.markdown('<div class="empty-box">No clinic data available.</div>', unsafe_allow_html=True)

        st.markdown('<div class="footer-note">Guardian Angel — AI-Powered Seizure Detection System v2.0</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading admin dashboard: {e}")
        st.info("Try refreshing the page or checking your database connection.")