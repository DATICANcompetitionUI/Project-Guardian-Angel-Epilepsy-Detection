
### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Frontend** | Streamlit (PWA) | 1.28+ |
| **Backend** | Python | 3.12+ |
| **ML Model** | TensorFlow/Keras | 2.13+ |
| **Database** | Firebase Realtime DB | - |
| **Auth** | Firebase Auth | - |
| **SMS** | Twilio API | 8.10+ |
| **Visualization** | Plotly | 5.17+ |
| **Explainability** | SHAP | 0.42+ |

### Model Specifications

| Parameter | Value |
|-----------|-------|
| Architecture | CNN + LSTM |
| Input Shape | (250, 6) |
| Parameters | 69,217 |
| Training Data | 20 patients, 886 seizures |
| Sensitivity | 63% |
| Specificity | 79% |
| False Alarm Reduction | 95% (with smoothing) |

---

## 3. Installation Guide

### Prerequisites

- Python 3.12 or higher
- Git
- Firebase Account (free tier)
- Twilio Account (optional, free trial)

### Step 1: Clone the Repository

```bash
git clone https://github.com/promivine-prog/guardian-angel.git
cd guardian-angel