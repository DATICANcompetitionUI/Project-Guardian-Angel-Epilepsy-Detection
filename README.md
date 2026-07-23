# 👼 Guardian Angel — AI-Powered Seizure Detection System

**An offline, smartphone-based epilepsy detection, prediction, and emergency response system.**

**🔗 Live Demo:** [guardian-angel-epilepsy-detection.streamlit.app](https://guardian-angel-epilepsy-detection.streamlit.app/)

> **Research prototype notice:** Guardian Angel is a competition/research prototype. It is not a certified medical device and should not replace a clinician-prescribed monitoring plan or emergency protocol.


## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Performance Metrics](#performance-metrics)
4. [Limitations & Future Work](#limitations--future-work)
5. [Milestones](#milestones)
6. [Technology Stack](#technology-stack)
7. [Installation Guide](#installation-guide)
8. [User Guide](#user-guide)
9. [Admin Guide](#admin-guide)
10. [Project Structure](#project-structure)
11. [Demo Accounts](#demo-accounts)
12. [License](#license)
13. [Acknowledgements](#acknowledgements)

---

## Project Overview

Guardian Angel is an AI-powered, offline-first smartphone application that uses phone motion sensors (accelerometer + gyroscope) to detect seizures in real time, predict seizure risk, and trigger an emergency response protocol.

**The problem:**
- ~50 million people worldwide live with epilepsy.
- An estimated 70% could live seizure-free with proper treatment and monitoring.
- Sudden Unexpected Death in Epilepsy (SUDEP) remains a major concern, and faster detection/response can help.

**Our approach:**
- Real-time seizure detection using only phone motion sensors — no wearables required
- AI-powered risk prediction with explainable (SHAP-based) output
- Automatic emergency response with GPS location sharing
- Offline-first design that works without an internet connection

---

## Key Features

| Feature | Description |
|---|---|
| 🧠 Real-time Detection | CNN+LSTM model trained on data from 20 real patients |
| 📊 Risk Prediction | Low / Moderate / High risk levels |
| 🛡️ Smart Alerts | Consecutive-window smoothing reduces false alarms by ~95% |
| 🆘 Welfare Check | Multi-stage escalation: user → caregiver → emergency |
| 💡 Explainable AI | SHAP highlights *why* a prediction was made, not just *what* it is |
| 📱 Offline PWA | Installable on a phone home screen, works without internet |
| 🚨 Emergency Response | SMS alerts with GPS location via Twilio |
| 👨‍⚕️ Admin Dashboard | Monitor all patients from a single dashboard |
| 🔐 Multi-User Auth | Secure login via Firebase Authentication |

---

## Performance Metrics

### Model Performance

| Metric | Value |
|---|---|
| Sensitivity (Recall) | 63% |
| Specificity | 79% |
| Precision (before smoothing) | 0.7% |
| Precision (after smoothing) | ~15% |
| False alarm reduction (via smoothing) | ~95% |
| Training data | 20 patients, 886 seizures (SeizeIT2) |

### Why these numbers matter

Seizure detection from motion sensors alone is a genuinely hard signal-processing problem, and raw precision before smoothing (0.7%) reflects that: without post-processing, the model would generate far more false alarms than true detections. Consecutive-window smoothing is what makes the system usable, raising precision roughly 20x — but the residual false-alarm rate (~85% of alerts) is still the system's biggest open limitation. See below.

---

## Limitations & Future Work

Being upfront about this is a deliberate design choice, not an oversight:

- **False alarm rate.** Even after smoothing, most alerts are still false positives. This is acceptable for a research prototype but not yet for unsupervised clinical deployment.
- **Training data size.** 20 patients is a reasonable start for a hackathon/competition timeline but too small to generalize across the population — larger, more diverse datasets are the next step.
- **Motion-only signal.** Relying solely on accelerometer + gyroscope (no EEG or ECG) trades accuracy for accessibility. Future versions could fuse in optional wearable ECG data for patients who have it.
- **Not a diagnostic device.** Guardian Angel is intended as a monitoring and alerting aid, not a replacement for clinical diagnosis or prescribed treatment.
- **PWA → native app.** The current PWA runs well for demo purposes, but a native Android/iOS build is planned next to enable background sensor sampling that survives app-switching and phone lock, tighter battery optimization, and more reliable OS-level notifications for alerts.

---

## Milestones

- **Milestone 1 — Data Pipeline & Windowing:** SeizeIT2 dataset (OpenNeuro ds005873), 20 patients, 886 seizures, 10s windows with 5s step, feature extraction, output to `data/seizeit2_windows.csv`.
- **Milestone 2 — Baseline ML Models:** Logistic Regression and Random Forest baselines with confusion-matrix comparison and end-to-end pipeline validation.
- **Milestone 3 — CNN+LSTM Detection:** 69,217-parameter CNN+LSTM model using motion sensors only, reaching 63% sensitivity / 79% specificity. Saved as `models/seizure_detection_model.h5`.
- **Milestone 4 — Monitoring Coverage & Welfare Check:** Monitoring coverage tracker, welfare check protocol, escalation logic (user → caregivers → emergency), 3-window consecutive smoothing.
- **Milestone 5 — Explainable AI (SHAP):** Feature importance analysis (top features: heart rate, accelerometer X, gyroscope Y), plain-language explanations, visualization at `evaluation/shap_analysis.png`.
- **Milestone 6 — Offline PWA:** Streamlit-based interface installable via "Add to Home Screen," with risk dashboard, monitoring coverage, welfare check, GPS integration, emergency contacts, and offline support via service worker.
- **Milestone 7 — Emergency Response & Evaluation:** Twilio SMS integration, real GPS sharing, full evaluation metrics, and end-to-end system testing.

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend | Streamlit (PWA) | 1.28+ |
| Backend | Python | 3.12+ |
| Machine Learning | TensorFlow/Keras | 2.13+ |
| Database | Firebase Realtime DB | — |
| Authentication | Firebase Auth | — |
| SMS | Twilio API | 8.10+ |
| Visualization | Plotly | 5.17+ |
| Explainability | SHAP | 0.42+ |
| Signal Processing | MNE, SciPy | 1.5+ |

---

## Installation Guide

### Prerequisites
- Python 3.12+
- Git
- A Firebase account (free tier)
- A Twilio account (optional, free trial)

### 1. Clone the repository
```bash
git clone https://github.com/promivine-prog/guardian-angel.git
cd guardian-angel
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Firebase
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Create a new project.
3. Enable Email/Password Authentication.
4. Create a Realtime Database (test mode).
5. Copy your config keys into `app/firebase_config.py`.

### 5. Configure environment variables
Create a `.env` file:
```env
# Firebase
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your_project-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID=your_project_id

# Twilio (optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

### 6. Run the app
```bash
streamlit run app/app.py
```

### 7. Install as a PWA on your phone
1. Open `http://localhost:8501` in Chrome.
2. Tap **Add to Home Screen**.
3. Use it like any other app.

---

## User Guide

### Creating an account
1. Open the app.
2. Click the **Sign Up** tab.
3. Fill in your details.
4. Select **user** or **admin** role.
5. Click **Create Account**, then log in.

### User dashboard

| Section | Description |
|---|---|
| Seizure Risk | 🟢 Low / 🟠 Moderate / 🔴 High |
| Monitoring | 🟢 Active / 🔴 Paused |
| Coverage | Percentage of time monitored |
| Total Alerts | Number of alerts received |
| Real-time Chart | Risk score and motion activity |
| Alert History | All past alerts |
| Quick Actions | "I'm Fine" / "Need Help" buttons |

### Emergency contacts
1. In the sidebar, find **Emergency Contacts**.
2. Enter contact phone numbers.
3. Save — contacts receive SMS alerts during emergencies.

### Welfare check flow
```text
Seizure Detected (automatic)
        ↓
User gets "Are You Okay?" prompt
        ↓
Wait 30 seconds
        ↓
No response? → Caregivers alerted via SMS
        ↓
Wait 60 seconds
        ↓
No response? → Emergency alert sent with GPS location
```

---

## Admin Guide

### Access
1. Create an account with role **admin**.
2. Log in with admin credentials.
3. Navigate to **Admin Dashboard**.

### Features

| Feature | Description |
|---|---|
| Metrics | Total users, high-risk count, active monitoring, total alerts |
| All Users Table | Name, email, role, risk, monitoring status, contacts |
| Filter Users | By role, risk, or monitoring status |
| Export Data | Download CSV of all users |
| Recent Alerts | View all alerts across users |

---

## Project Structure

```text
guardian_angel/
├── app/
│   ├── app.py                     # Main Streamlit app
│   ├── auth.py                    # Firebase authentication
│   ├── admin_dashboard.py         # Admin panel
│   ├── firebase_config.py         # Firebase configuration
│   └── __init__.py                # Package init
├── models/
│   └── seizure_detection_model.h5 # Trained CNN+LSTM model
├── evaluation/
│   ├── shap_analysis.png          # SHAP visualization
│   └── shap_explanations.json     # Feature importance
├── preprocessing/
│   └── windowing.py               # Data pipeline
├── data/
│   └── seizeit2_windows.csv       # Processed features
├── .streamlit/
│   └── config.toml                # Streamlit config
├── SYSTEM_MANUAL.md               # Complete system manual
├── README.md                      # This file
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
└── .gitignore                      # Git ignore
```

---

## Demo Accounts

> ⚠️ These are sandbox credentials for a demo Firebase project only — no real patient data is associated with them. Rotate or remove before making the repository public if that changes.

| Role | Email | Password |
|---|---|---|
| Admin | `admin@guardian.com` | `admin123` |
| User | `user@guardian.com` | `user123` |

---

## Competition Submission

**What makes this project distinctive:**
- Trained on real clinical data — SeizeIT2, 886 real seizures across 20 patients
- Explainable AI: SHAP surfaces *why* a prediction was made
- Consecutive-window smoothing cuts false alarms by ~95%
- Multi-stage welfare check protocol (user → caregiver → emergency)
- Offline-first design, no internet required
- Phone-only — no expensive wearables
- Multi-user support with separate admin and user dashboards

**How judges can test it:**
1. Visit the live demo: [guardian-angel-epilepsy-detection.streamlit.app](https://guardian-angel-epilepsy-detection.streamlit.app/) — no installation needed.
2. Use the sidebar to simulate different risk levels.
3. Test the welfare check protocol end-to-end.
4. Review SHAP explanations in the dashboard.
5. Install as a PWA on a phone directly from the live link.

*(Alternatively, run locally with `streamlit run app/app.py` — see [Installation Guide](#installation-guide).)*

---

## License

MIT License — free for academic and research use.

---

## Acknowledgements

- [SeizeIT2 Dataset](https://openneuro.org/datasets/ds005873) (OpenNeuro) — clinical seizure data
- Streamlit — PWA framework and dashboard
- TensorFlow — deep learning framework
- SHAP — model explainability
- Twilio — SMS emergency alerts
- Firebase — authentication and database
- Plotly — interactive visualizations

---

## Version History

| Version | Date | Changes |
|---|---|---|
| v2.0 | 2026-07-15 | Full production release with Firebase + Admin Dashboard |
| v1.0 | 2026-07-10 | Initial release with all 7 milestones |

---

## Contact

- GitHub: [promivine-prog/guardian-angel](https://github.com/promivine-prog/guardian-angel)
- Issues: open a GitHub issue
- Email: promivine@gmail.com

---

**Guardian Angel — Saving Lives with AI**
*DATICAN AI in Medicine Competition 2026 — University of Ibadan, Nigeria*
