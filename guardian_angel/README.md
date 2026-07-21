# 👼 Guardian Angel - AI-Powered Seizure Detection System

**An AI-powered offline smartphone-based epilepsy detection, prediction, and emergency response system.**

[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://guardian-angel.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Performance Metrics](#performance-metrics)
4. [Milestones](#milestones)
5. [Technology Stack](#technology-stack)
6. [Installation Guide](#installation-guide)
7. [User Guide](#user-guide)
8. [Project Structure](#project-structure)
9. [Demo Accounts](#demo-accounts)
10. [License](#license)
11. [Acknowledgements](#acknowledgements)

---

## 🏆 Project Overview

Guardian Angel is an **AI-powered offline smartphone-based epilepsy detection, prediction, and emergency response system**. It uses phone motion sensors (accelerometer + gyroscope) to detect seizures in real-time, predict seizure risk, and initiate emergency protocols.

### The Problem

- **50 million people** worldwide have epilepsy
- **70%** could live seizure-free with proper treatment
- **Sudden Unexpected Death in Epilepsy (SUDEP)** is a major concern
- **Real-time detection** can save lives

### Our Solution

Guardian Angel provides:
- ✅ **Real-time seizure detection** using phone motion sensors
- ✅ **AI-powered risk prediction** with explainable results
- ✅ **Automatic emergency response** with GPS location sharing
- ✅ **Offline-first design** — works without internet
- ✅ **No expensive wearables** — just your phone

---

## 🎯 Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **🧠 Real-time Detection** | CNN+LSTM model trained on 20 real patients | ✅ |
| **📊 Risk Prediction** | Low/Moderate/High risk levels | ✅ |
| **🛡️ Smart Alerts** | Consecutive-window smoothing reduces false alarms by 95% | ✅ |
| **🆘 Welfare Check** | Multi-stage escalation (user → caregiver → emergency) | ✅ |
| **💡 Explainable AI** | SHAP tells WHY, not just WHAT | ✅ |
| **📱 Offline PWA** | Works without internet, installable on phone | ✅ |
| **🚨 Emergency Response** | SMS alerts with GPS location via Twilio | ✅ |
| **👨‍⚕️ Admin Dashboard** | Monitor all patients from one dashboard | ✅ |
| **🔐 Multi-User Auth** | Secure login with Firebase | ✅ |

---

## 📊 Performance Metrics

### Model Performance

| Metric | Value |
|--------|-------|
| **Sensitivity (Recall)** | 63% |
| **Specificity** | 79% |
| **Precision (Before Smoothing)** | 0.7% |
| **Precision (After Smoothing)** | ~15% |
| **False Alarm Reduction** | 95% |
| **Training Data** | 20 patients, 886 seizures |

### Clinical Relevance

- ✅ Trained on real clinical data (SeizeIT2)
- ✅ Model explains decisions via SHAP
- ✅ Phone-based = accessible to everyone
- ✅ Offline-first = works without internet
- ✅ Consecutive-window smoothing = 95% fewer false alarms

---

## 🎓 Milestones

### ✅ Milestone 1 — Data Pipeline & Windowing
- Dataset: SeizeIT2 (OpenNeuro ds005873)
- 20 real patients with 886 seizures
- Signal cleaning and windowing (10s windows, 5s step)
- Feature extraction (mean/std/min/max per signal)
- Processed CSV output: `data/seizeit2_windows.csv`

### ✅ Milestone 2 — Baseline ML Models
- Logistic Regression
- Random Forest
- Performance comparison with confusion matrix
- End-to-end pipeline validation

### ✅ Milestone 3 — CNN+LSTM Seizure Detection
- CNN+LSTM architecture (69,217 parameters)
- Motion-sensor-only detection (Accel + Gyro)
- 63% sensitivity, 79% specificity
- Model saved: `models/seizure_detection_model.h5`

### ✅ Milestone 4 — Monitoring Coverage & Welfare Check
- Monitoring Coverage Tracker
- Welfare Check Protocol
- Escalation: User → Caregivers → Emergency
- Consecutive-window smoothing (3 consecutive windows)

### ✅ Milestone 5 — Explainable AI (SHAP)
- SHAP feature importance analysis
- Top features: ECG (Heart Rate), Accelerometer X, Gyroscope Y
- Plain-language explanations
- Visualization: `evaluation/shap_analysis.png`

### ✅ Milestone 6 — Offline PWA App
- Streamlit-based interface
- Installable via "Add to Home Screen"
- Risk Dashboard, Monitoring Coverage, Welfare Check
- GPS integration, Emergency Contacts
- Seizure/risk history
- Service worker for offline support

### ✅ Milestone 7 — Emergency Response & Evaluation
- Twilio SMS integration
- Real GPS sharing
- Evaluation metrics
- Complete system testing

---

## 🛠️ Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Frontend** | Streamlit (PWA) | 1.28+ |
| **Backend** | Python | 3.12+ |
| **Machine Learning** | TensorFlow/Keras | 2.13+ |
| **Database** | Firebase Realtime DB | - |
| **Authentication** | Firebase Auth | - |
| **SMS** | Twilio API | 8.10+ |
| **Visualization** | Plotly | 5.17+ |
| **Explainability** | SHAP | 0.42+ |
| **Signal Processing** | MNE, SciPy | 1.5+ |

---

## 🚀 Installation Guide

### Prerequisites

- Python 3.12+
- Git
- Firebase Account (free tier)
- Twilio Account (optional, free trial)

### Step 1: Clone the Repository

```bash
git clone https://github.com/promivine-prog/guardian-angel.git
cd guardian-angel