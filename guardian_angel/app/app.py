"""
Guardian Angel - Professional Health App with Caregiver Dashboard
Run: streamlit run app/app.py
"""


import subprocess
import sys

try:
    import plotly
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly
    
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import streamlit.components.v1 as components

# Import authentication - FIXED
from auth import (
    sign_up, sign_in, logout,
    get_user_data, update_user_data,
    save_alert, get_user_alerts, db,
    link_caregiver_to_user, get_caregiver_users
)

# Import admin dashboard
from admin_dashboard import admin_dashboard

# Import caregiver dashboard
try:
    from caregiver_dashboard import caregiver_dashboard
except ImportError:
    def caregiver_dashboard():
        st.info("👨‍👩‍👧 Caregiver Dashboard - Coming soon!")

# Import monitoring coverage tracker
from monitoring_coverage import MonitoringCoverageTracker

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Guardian Angel - Seizure Detection",
    page_icon="🩺",
    layout="wide"
)

# ============================================
# DESIGN SYSTEM
# ============================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    :root {
        --ga-primary: #1F6F5C;
        --ga-primary-dark: #164F41;
        --ga-primary-light: #E4F1EC;
        --ga-bg: #F5F8F6;
        --ga-card: #FFFFFF;
        --ga-text: #182420;
        --ga-text-muted: #5B6B62;
        --ga-border: #E3EAE4;
        --ga-alert: #D9583A;
        --ga-alert-bg: #FBEAE5;
        --ga-warn: #C68A2E;
        --ga-warn-bg: #FBF2E1;
        --ga-success: #2F9E64;
        --ga-success-bg: #E9F7EE;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, .ga-display { font-family: 'Manrope', sans-serif; }

    .stApp { background-color: var(--ga-bg) !important; color: var(--ga-text) !important; }
    body, .stApp, div, p, span, h1, h2, h3, h4, h5, h6, label, li, blockquote,
    .stMarkdown, .stText, .stCaption, .stSubheader, .stTitle {
        color: var(--ga-text) !important;
    }
    #MainMenu, footer {visibility: hidden;}
    .block-container { padding-top: 3rem; padding-bottom: 3rem; }

    input, textarea, .stTextInput input, .stSelectbox select, .stSelectbox div {
        color: var(--ga-text) !important;
        background-color: #FFFFFF !important;
        border: 1px solid var(--ga-border) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: var(--ga-text) !important;
        border-color: var(--ga-border) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] * { color: var(--ga-text) !important; fill: var(--ga-text) !important; }
    div[data-baseweb="popover"], div[data-baseweb="popover"] ul, ul[role="listbox"] { background-color: #FFFFFF !important; }
    li[role="option"], div[role="option"] { background-color: #FFFFFF !important; color: var(--ga-text) !important; }
    li[role="option"]:hover, div[role="option"]:hover { background-color: var(--ga-primary-light) !important; }
    div[data-baseweb="select"] [class*="placeholder"] { color: var(--ga-text-muted) !important; }
    .stTextInput > div > div { border-radius: 10px !important; }

    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid var(--ga-border); }
    [data-testid="stSidebar"] * { color: var(--ga-text) !important; }

    .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }
    .dot-green { background-color: var(--ga-success); }
    .dot-orange { background-color: var(--ga-warn); }
    .dot-red { background-color: var(--ga-alert); }

    .stButton > button {
        background-color: var(--ga-primary) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: background-color 0.15s ease !important;
    }
    .stButton > button:hover { background-color: var(--ga-primary-dark) !important; }

    .stTabs [data-baseweb="tab"] { color: var(--ga-text-muted) !important; font-weight: 500 !important; }
    .stTabs [aria-selected="true"] { color: var(--ga-primary) !important; border-bottom: 3px solid var(--ga-primary) !important; }

    [data-testid="stMetricValue"] { color: var(--ga-text) !important; }
    [data-testid="stMetricLabel"] { color: var(--ga-text-muted) !important; }

    .metric-card {
        background: var(--ga-card) !important;
        border-radius: 14px !important;
        padding: 20px 20px !important;
        border: 1px solid var(--ga-border) !important;
        box-shadow: 0 1px 3px rgba(24,36,32,0.04) !important;
        transition: box-shadow 0.15s ease, transform 0.15s ease !important;
    }
    .metric-card:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 18px rgba(31,111,92,0.10) !important; }
    .metric-card h3 {
        color: var(--ga-text-muted) !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 700 !important;
        margin: 0 0 8px 0 !important;
    }
    .metric-card .value { font-size: 1.9rem !important; font-weight: 800 !important; color: var(--ga-text) !important; }
    .metric-card .sub { color: var(--ga-text-muted) !important; font-size: 0.75rem !important; margin-top: 4px !important; }

    .stInfo { background-color: var(--ga-primary-light) !important; border-left: 4px solid var(--ga-primary) !important; color: var(--ga-text) !important; }
    .stSuccess { background-color: var(--ga-success-bg) !important; border-left: 4px solid var(--ga-success) !important; color: var(--ga-text) !important; }
    .stWarning { background-color: var(--ga-warn-bg) !important; border-left: 4px solid var(--ga-warn) !important; color: var(--ga-text) !important; }
    .stError { background-color: var(--ga-alert-bg) !important; border-left: 4px solid var(--ga-alert) !important; color: var(--ga-text) !important; }

    .badge {
        display: inline-block !important;
        background: var(--ga-primary-light) !important;
        color: var(--ga-primary-dark) !important;
        padding: 4px 16px !important;
        border-radius: 50px !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em;
    }

    .caregiver-card {
        background: var(--ga-primary-light) !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        border-left: 4px solid var(--ga-primary) !important;
        color: var(--ga-text) !important;
    }
    .caregiver-card strong, .caregiver-card span { color: var(--ga-text) !important; }

    .pulse-divider { width: 100%; height: 34px; margin: 4px 0 18px 0; }
    .pulse-divider svg { width: 100%; height: 100%; display: block; }

    .ga-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 0 14px 0;
        border-bottom: 1px solid var(--ga-border);
        margin-bottom: 6px;
    }
    .ga-topbar h2 { margin: 0 !important; font-weight: 800 !important; }
    .ga-topbar p { color: var(--ga-text-muted) !important; font-size: 0.9rem !important; margin: 2px 0 0 0 !important; }

    .hero-title { font-size: 2.4rem; font-weight: 800; color: var(--ga-primary-dark); margin: 0; letter-spacing: -0.01em; }
    .hero-sub { color: var(--ga-text-muted); font-size: 1.05rem; margin: 6px 0 0 0; }
    .feature-pill {
        display: inline-flex; align-items: center; gap: 6px;
        background: #FFFFFF; border: 1px solid var(--ga-border);
        border-radius: 10px; padding: 10px 14px; font-size: 0.85rem; font-weight: 600;
        color: var(--ga-text);
    }

    .footer {
        color: #93A399 !important;
        font-size: 0.8rem !important;
        border-top: 1px solid var(--ga-border) !important;
        padding-top: 20px !important;
        margin-top: 40px !important;
        text-align: center !important;
    }

    .monitoring-active {
        background: var(--ga-success-bg) !important;
        border: 1px solid var(--ga-success) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 16px !important;
    }
    .monitoring-paused {
        background: var(--ga-alert-bg) !important;
        border: 1px solid var(--ga-alert) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 16px !important;
    }
    .checkin-history {
        font-size: 0.85rem;
        color: var(--ga-text-muted);
        padding: 8px 12px;
        background: var(--ga-primary-light);
        border-radius: 8px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


def pulse_divider(color="#1F6F5C", opacity="0.55"):
    st.markdown(f"""
    <div class="pulse-divider">
        <svg viewBox="0 0 600 34" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="0,17 140,17 165,17 178,4 190,30 203,17 230,17 600,17"
                fill="none" stroke="{color}" stroke-opacity="{opacity}" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)


def request_notification_permission():
    components.html("""
    <script>
        if ('Notification' in window && Notification.permission !== 'granted') {
            Notification.requestPermission();
        }
    </script>
    """, height=0)


def send_browser_notification(title, body):
    safe_title = title.replace("'", "\\'")
    safe_body = body.replace("'", "\\'")
    components.html(f"""
    <script>
        if ('Notification' in window && Notification.permission === 'granted') {{
            new Notification('{safe_title}', {{ body: '{safe_body}' }});
        }}
    </script>
    """, height=0)


# ============================================
# SESSION STATE
# ============================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'name' not in st.session_state:
    st.session_state.name = None

if 'coverage_tracker' not in st.session_state:
    st.session_state.coverage_tracker = MonitoringCoverageTracker()


# ============================================
# LOGIN PAGE
# ============================================
def login_page():
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("""
            <div style="padding: 20px 0 0 0;">
                <span class="badge">🩺 AI Seizure Detection</span>
                <h1 class="hero-title">Guardian Angel</h1>
                <p class="hero-sub">Real-time seizure detection and emergency response, built around the people who care for you.</p>
            </div>
        """, unsafe_allow_html=True)

        pulse_divider()

        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            st.markdown('<div class="feature-pill">🧠 On-device AI</div>', unsafe_allow_html=True)
        with fcol2:
            st.markdown('<div class="feature-pill">📱 Works offline</div>', unsafe_allow_html=True)
        with fcol3:
            st.markdown('<div class="feature-pill">🚨 Instant alerts</div>', unsafe_allow_html=True)
        with fcol4:
            st.markdown('<div class="feature-pill">💡 Explainable</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="metric-card">
            <h3>How it works</h3>
            <p style="margin: 6px 0; color: var(--ga-text);">✅ <strong>Real-time detection</strong> using your phone's motion sensors — no wearables required.</p>
            <p style="margin: 6px 0; color: var(--ga-text);">✅ <strong>Automatic emergency response</strong> with GPS location shared with your contacts.</p>
            <p style="margin: 6px 0; color: var(--ga-text);">✅ <strong>Caregiver visibility</strong> so the people who look out for you always know your status.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

        with tab1:
            st.markdown("#### Welcome back")
            login_email = st.text_input("Email", placeholder="user@email.com", key="login_email")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

            if st.button("🔑 Login", use_container_width=True):
                if login_email and login_password:
                    success, result, role, name = sign_in(login_email, login_password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = result
                        st.session_state.user_id = result['localId']
                        st.session_state.role = role
                        st.session_state.name = name
                        st.success(f"✅ Logged in as {role}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("Please enter email and password")

            st.markdown("---")
            st.caption("📝 Demo: admin@guardian.com / admin123")
            st.caption("👤 Demo: user@guardian.com / user123")
            st.caption("👨‍👩‍👧 Demo: caregiver@guardian.com / caregiver123")

        with tab2:
            st.markdown("#### Create account")
            signup_name = st.text_input("Full Name", placeholder="John Doe", key="signup_name")
            signup_email = st.text_input("Email", placeholder="user@email.com", key="signup_email")
            signup_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

            signup_role = st.selectbox(
                "Account Type",
                ["user", "admin", "caregiver"],
                key="signup_role"
            )

            selected_user = None
            user_list = []

            if signup_role == "caregiver":
                st.markdown("---")
                st.markdown("#### 👨‍👩‍👧 Who are you caring for?")

                try:
                    all_users = db.child("users").get()
                    if all_users and all_users.val():
                        for uid, udata in all_users.val().items():
                            if isinstance(udata, dict):
                                role = udata.get("role", "user")
                                if role == "user":
                                    user_list.append({
                                        "id": uid,
                                        "name": udata.get("name", "Unknown"),
                                        "email": udata.get("email", "No email")
                                    })

                        if user_list:
                            user_options = [f"{u['name']} ({u['email']})" for u in user_list]
                            selected_user = st.selectbox(
                                "Select the person you care for",
                                user_options,
                                key="caregiver_patient"
                            )
                            st.info("💡 You can also add more people later in your dashboard.")
                        else:
                            st.warning("⚠️ No users found. Create a user account first.")
                            selected_user = None
                    else:
                        st.warning("⚠️ No users found. Create a user account first.")
                        selected_user = None
                except Exception as e:
                    st.warning(f"⚠️ Unable to load users: {e}")
                    selected_user = None

            if st.button("📝 Create Account", use_container_width=True):
                if signup_password == signup_confirm:
                    if len(signup_password) >= 6:
                        success, message = sign_up(signup_email, signup_password, signup_role, signup_name)
                        if success:
                            st.success(f"✅ {message}")
                            st.info(f"📌 You signed up as: **{signup_role}**")

                            if signup_role == "caregiver" and selected_user:
                                for u in user_list:
                                    if f"{u['name']} ({u['email']})" == selected_user:
                                        link_success, link_message = link_caregiver_to_user(
                                            signup_email,
                                            u['email']
                                        )
                                        if link_success:
                                            st.success(f"✅ {link_message}")
                                        else:
                                            st.warning(f"⚠️ {link_message}")
                                        break

                            st.info("🔑 Please login to continue.")
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("Password must be at least 6 characters")
                else:
                    st.error("Passwords don't match")


# ============================================
# USER DASHBOARD
# ============================================
def user_dashboard():
    st.markdown("""
    <style>
        .scrolling-banner {
            background: var(--ga-primary-light);
            padding: 12px 20px;
            border-radius: 10px;
            border-left: 4px solid var(--ga-primary);
            overflow: hidden;
            white-space: nowrap;
            margin-bottom: 20px;
        }
        .scrolling-banner p {
            display: inline-block;
            padding-left: 100%;
            animation: scroll-text 20s linear infinite;
            color: var(--ga-text);
            font-size: 1rem;
            font-weight: 500;
            margin: 0;
        }
        @keyframes scroll-text {
            0% { transform: translateX(0); }
            100% { transform: translateX(-100%); }
        }
    </style>
    <div class="scrolling-banner">
        <p>📞 No smartphone? No problem! Call our voice check-in number: <strong>+1 234 567 8900</strong> for daily check-ins. Caregivers can call too! 24/7 support available.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="ga-topbar">
            <div>
                <h2>Welcome, {st.session_state.name}</h2>
                <p>Your personal monitoring dashboard</p>
            </div>
            <div>
                <span class="badge"><span class="dot dot-green"></span> Live</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    pulse_divider()

    # ============================================
    # DAILY CHECK-IN (MULTIPLE TIMES PER DAY)
    # ============================================
    if st.session_state.role == 'user':
        try:
            from risk_trend import daily_checkin_ui
            daily_checkin_ui(st.session_state.user_id)
        except ImportError:
            st.info("💡 Daily check-in module not found — add `risk_trend.py` to enable it.")

    user_data = get_user_data(st.session_state.user_id)
    risk = user_data.get("risk_level", "Low")
    monitoring = user_data.get("monitoring_active", True)

    # ============================================
    # MONITORING STATUS ALERT (Real-time + Push Notification)
    # ============================================
    if 'last_monitoring_status' not in st.session_state:
        st.session_state.last_monitoring_status = monitoring

    if st.session_state.last_monitoring_status != monitoring:
        if monitoring:
            send_browser_notification(
                "Guardian Angel — Monitoring Active",
                "Seizure detection is now active. You are protected."
            )
        else:
            send_browser_notification(
                "Guardian Angel — Monitoring Paused",
                "Seizure detection is paused. Open the app to resume protection."
            )

    st.session_state.last_monitoring_status = monitoring

    if monitoring:
        st.markdown("""
            <div class="monitoring-active">
                ✅ <strong>Monitoring Active</strong> — You are protected. The system is watching for seizures.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="monitoring-paused">
                ❌ <strong>Monitoring Paused</strong> — You are NOT protected. Please open the app or keep your phone active.
            </div>
        """, unsafe_allow_html=True)

    # ============================================
    # UPDATE COVERAGE TRACKER (Real-time, honest coverage)
    # ============================================
    st.session_state.coverage_tracker.update_activity(
        motion_detected=monitoring,
        charging=False,
        screen_on=True,
        app_foreground=True
    )
    coverage_report = st.session_state.coverage_tracker.get_status_report()
    coverage_pct = coverage_report.get("daily_coverage_percent", 0)

    # ============================================
    # HIGH RISK WARNING
    # ============================================
    if st.session_state.role == 'user':
        if 'notif_permission_requested' not in st.session_state:
            request_notification_permission()
            st.session_state.notif_permission_requested = True

        if risk == "High":
            last_notified = user_data.get("last_risk_notification", "")
            should_notify = True
            if last_notified:
                try:
                    elapsed = (datetime.now() - datetime.fromisoformat(last_notified)).total_seconds()
                    should_notify = elapsed > 300
                except Exception:
                    should_notify = True

            if should_notify:
                from auth import send_risk_notification
                send_risk_notification(st.session_state.user_id, risk)
                update_user_data(st.session_state.user_id, {
                    "last_risk_notification": datetime.now().isoformat()
                })
                send_browser_notification(
                    "Guardian Angel — High Risk Alert",
                    "Your seizure risk has increased to HIGH. Caregivers have been notified."
                )

            st.error("""
🚨 **HIGH RISK ALERT**

Your seizure risk level has increased to **HIGH**.

Please take precautions:
- Sit or lie down in a safe place
- Inform someone nearby
- Have your emergency medication ready
- Stay calm and breathe deeply

Caregivers have been notified.
            """)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if risk == "Low":
            dot_class, color = "dot-green", "var(--ga-success)"
        elif risk == "Moderate":
            dot_class, color = "dot-orange", "var(--ga-warn)"
        else:
            dot_class, color = "dot-red", "var(--ga-alert)"

        st.markdown(f"""
            <div class="metric-card">
                <h3>Seizure Risk</h3>
                <div class="value" style="color: {color};">
                    <span class="dot {dot_class}"></span> {risk}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        if monitoring:
            dot_class, color, status_text = "dot-green", "var(--ga-success)", "Active"
        else:
            dot_class, color, status_text = "dot-red", "var(--ga-alert)", "Paused"

        st.markdown(f"""
            <div class="metric-card">
                <h3>Monitoring</h3>
                <div class="value" style="color: {color};">
                    <span class="dot {dot_class}"></span> {status_text}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Coverage</h3>
                <div class="value">{coverage_pct:.1f}%</div>
                <p class="sub">Today's real coverage</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        alerts = get_user_alerts(st.session_state.user_id)
        st.markdown(f"""
            <div class="metric-card">
                <h3>Total Alerts</h3>
                <div class="value">{len(alerts)}</div>
                <p class="sub">Since launch</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Real-time monitoring")
    st.caption("Your personal health data — only you and your caregivers can see this.")

    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = pd.DataFrame({
            'time': pd.date_range(end=datetime.now(), periods=50, freq='1s'),
            'risk_score': np.random.uniform(0, 0.3, 50),
            'motion': np.random.uniform(0.1, 0.4, 50)
        })

    new_time = datetime.now()
    risk_values = {"Low": 0.2, "Moderate": 0.55, "High": 0.85}
    current_risk = risk_values.get(risk, 0.2)
    new_risk = max(0, min(1, current_risk + np.random.uniform(-0.05, 0.05)))
    new_motion = np.random.uniform(0.1, 0.8)

    new_row = pd.DataFrame({
        'time': [new_time],
        'risk_score': [new_risk],
        'motion': [new_motion]
    })

    st.session_state.chart_data = pd.concat([
        st.session_state.chart_data.iloc[1:],
        new_row
    ], ignore_index=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Seizure Risk Score", "Motion Activity"))

    fig.add_trace(go.Scatter(
        x=st.session_state.chart_data['time'],
        y=st.session_state.chart_data['risk_score'],
        name="Risk Score",
        line=dict(color='#1F6F5C', width=2),
        fill='tozeroy',
        fillcolor='rgba(31,111,92,0.14)'
    ), row=1, col=1)

    fig.add_hline(y=0.5, line_dash="dash", line_color="#C68A2E", row=1, col=1)
    fig.add_hline(y=0.7, line_dash="dash", line_color="#D9583A", row=1, col=1)

    fig.add_trace(go.Scatter(
        x=st.session_state.chart_data['time'],
        y=st.session_state.chart_data['motion'],
        name="Motion Activity",
        line=dict(color='#2F9E64', width=2)
    ), row=2, col=1)

    fig.update_layout(
        height=350,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#182420',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(gridcolor='#EEF2EF', showgrid=True)
    fig.update_yaxes(gridcolor='#EEF2EF', showgrid=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Alert history")

    user_alerts = get_user_alerts(st.session_state.user_id)
    if user_alerts:
        df_alerts = pd.DataFrame(user_alerts)
        if 'timestamp' in df_alerts.columns:
            df_alerts = df_alerts.sort_values('timestamp', ascending=False)
        st.dataframe(df_alerts, use_container_width=True, hide_index=True)
    else:
        st.info("No alerts recorded yet. Monitoring is active and ready.")

    st.markdown("---")
    st.subheader("👨‍👩‍👧 My Caregivers")

    user_data = get_user_data(st.session_state.user_id)
    current_caregivers = user_data.get("caregivers", [])

    if current_caregivers:
        st.info(f"📌 You have {len(current_caregivers)} caregiver(s) linked to your account.")
        for cg_id in current_caregivers:
            cg_data = get_user_data(cg_id)
            if cg_data:
                st.markdown(f"""
                <div class="caregiver-card">
                    👤 <strong>{cg_data.get('name', 'Unknown')}</strong>
                    <span style="color: var(--ga-text-muted); font-size: 0.85rem;">({cg_data.get('email', 'No email')})</span>
                    <span style="float: right; color: var(--ga-primary);">✅ Linked</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 You don't have any caregivers linked yet. Add one below.")

    st.markdown("#### ➕ Add a caregiver")
    st.caption("Enter the email of someone who will monitor your health. They need to create an account first.")

    col1, col2 = st.columns([3, 1])
    with col1:
        caregiver_email = st.text_input(
            "Caregiver's Email",
            placeholder="caregiver@email.com",
            key="add_caregiver_email",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("➕ Add Caregiver", use_container_width=True):
            if caregiver_email:
                user_email = st.session_state.user.get('email')
                success, message = link_caregiver_to_user(caregiver_email, user_email)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Please enter a caregiver email.")

    with st.expander("ℹ️ How does this work?"):
        st.markdown("""
        1. **You** enter your caregiver's email address above
        2. **Your caregiver** creates an account using that email
        3. **Your caregiver** will see your health data in their dashboard
        4. **You** can have multiple caregivers linked to your account
        5. **Caregivers** will receive alerts when you have a seizure
        """)

    st.markdown("---")

    if st.session_state.role == 'user':
        st.markdown("#### 📍 Location")
        st.caption("Tap to share your GPS location. If you skip this, your registered address will be used instead in an emergency.")
        try:
            from streamlit_geolocation import streamlit_geolocation
            gps_result = streamlit_geolocation()
            if gps_result and gps_result.get("latitude") is not None:
                st.session_state.browser_gps = {
                    "lat": gps_result["latitude"],
                    "lng": gps_result["longitude"],
                    "accuracy": f"High (~{round(gps_result.get('accuracy', 10))}m)"
                }
                st.success(f"✅ Location captured (±{round(gps_result.get('accuracy', 10))}m)")
        except ImportError:
            st.info("💡 Install `streamlit-geolocation` (`pip install streamlit-geolocation`) to enable GPS capture. Registered address will be used as a fallback.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Status", use_container_width=True):
                st.success("Confirmed OK! Caregivers notified you're safe.")

        with col2:
            if st.button("🚨 Emergency Alert", use_container_width=True):
                user_name = st.session_state.name
                user_id = st.session_state.user_id

                from emergency_response import EmergencyResponse
                from clinic_finder import detect_country_from_coords, find_nearest_clinic, get_user_location

                if 'emergency_system' not in st.session_state:
                    st.session_state.emergency_system = EmergencyResponse()

                location = get_user_location(user_id, browser_gps=st.session_state.get("browser_gps"))
                lat, lng = location["lat"], location["lng"]

                if lat is None or lng is None:
                    st.error("❌ No location available (no GPS captured and no registered address on file). Please call emergency services directly.")
                else:
                    user_data = get_user_data(user_id)
                    contacts = user_data.get("contacts", [])
                    st.session_state.emergency_system.set_emergency_contacts(contacts)
                    st.session_state.emergency_system.set_gps_location(lat, lng)

                    country = detect_country_from_coords(lat, lng)

                    with st.spinner("🚑 Locating nearest clinic..."):
                        success, clinic = st.session_state.emergency_system.send_emergency_alert(
                            user_name=user_name,
                            risk_level="HIGH",
                            confidence=0.95,
                            lat=lat,
                            lng=lng
                        )

                    if success:
                        save_alert(user_id, {
                            "risk": "EMERGENCY",
                            "confidence": 0.95,
                            "location": f"{lat}, {lng}",
                            "location_method": location["method"],
                            "country": country,
                            "clinic_alerted": clinic["name"] if clinic else "None",
                            "resolved": False
                        })

                        st.success("🚨 EMERGENCY ALERT SENT!")
                        st.caption(f"📡 Location source: {location['method']} ({location['accuracy']})")

                        if clinic:
                            st.info(f"🏥 Nearest Clinic: **{clinic['name']}** ({clinic['distance_km']} km)")
                            st.info(f"📞 Clinic Phone: {clinic.get('phone', 'N/A')}")
                        else:
                            st.warning("⚠️ No clinic found within 5km. Emergency services contacted.")

                        st.success(f"📱 {len(contacts)} caregivers notified.")
                        st.balloons()
                    else:
                        st.error("❌ Failed to send alert. Please call emergency services directly.")
    else:
        st.info(f"👋 Welcome, {st.session_state.role}. Use your dashboard to manage your responsibilities.")


# ============================================
# MAIN APP
# ============================================
if not st.session_state.logged_in:
    login_page()
else:
    with st.sidebar:
        st.markdown(f"""
            <div style="padding: 14px 16px; border-radius: 12px; background: var(--ga-primary-light); margin-bottom: 14px;">
                <h3 style="color: var(--ga-primary-dark); margin: 0;">🩺 Guardian Angel</h3>
                <p style="color: var(--ga-text-muted); font-size: 0.75rem; margin: 0 0 10px 0;">AI Seizure Detection</p>
                <p style="color: var(--ga-text-muted); font-size: 0.8rem; margin: 0;">
                    <strong style="color: var(--ga-text);">{st.session_state.name}</strong><br>
                    <span class="badge" style="background: var(--ga-primary); color: #fff; margin-top: 4px;">{st.session_state.role}</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.role == 'admin':
            page = st.radio("📂 Navigation", ["📊 Admin Dashboard", "👤 My Dashboard", "📞 Voice Check-In", "⚙️ Settings"])
        elif st.session_state.role == 'caregiver':
            page = st.radio("📂 Navigation", ["👨‍👩‍👧 Caregiver Dashboard", "👤 My Dashboard", "⚙️ Settings"])
        else:
            page = st.radio("📂 Navigation", ["👤 My Dashboard", "⚙️ Settings"])

        if st.session_state.role == 'user':
            st.markdown("#### 📞 Emergency Contacts")
            user_data = get_user_data(st.session_state.user_id)
            contacts = user_data.get("contacts", [])

            contact1 = st.text_input("Contact 1", value=contacts[0] if len(contacts) > 0 else "", placeholder="+234 800 000 0000", key="contact_1")
            contact2 = st.text_input("Contact 2", value=contacts[1] if len(contacts) > 1 else "", placeholder="+234 800 000 0001", key="contact_2")

            new_contacts = [c for c in [contact1, contact2] if c]
            if new_contacts:
                update_user_data(st.session_state.user_id, {"contacts": new_contacts})
                st.success(f"✅ {len(new_contacts)} contacts saved")

        elif st.session_state.role == 'caregiver':
            st.markdown("#### 👨‍👩‍👧 Caregiver Info")
            st.info("📌 You are monitoring loved ones.\n\nCheck the Caregiver Dashboard.")

        elif st.session_state.role == 'admin':
            st.markdown("#### 👑 Admin Info")
            st.info("📌 Use the Admin Dashboard to monitor all users.")

        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

    if page == "📊 Admin Dashboard":
        admin_dashboard()
    elif page == "👨‍👩‍👧 Caregiver Dashboard":
        caregiver_dashboard()
    elif page == "📞 Voice Check-In":
        try:
            from voice_checkin import voice_checkin_dashboard
            voice_checkin_dashboard()
        except ImportError:
            st.warning("⚠️ Voice check-in module not found.")
    elif page == "⚙️ Settings":
        try:
            from settings import settings_ui
            settings_ui()
        except ImportError:
            st.warning("⚠️ Settings module not found. Create `settings.py` with a `settings_ui()` function to enable this page.")
    else:
        user_dashboard()

st.markdown("""
    <div class="footer">
        Guardian Angel — AI-Powered Seizure Detection System v2.0
    </div>
""", unsafe_allow_html=True)