<<<<<<< HEAD
# 🛡️ SentinelAPI – Secure API Monitoring & Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![ML](https://img.shields.io/badge/Machine%20Learning-Enabled-purple)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
=======
# 🚀 SentinelAPI – Secure API Monitoring & Protection Platform  

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

<<<<<<< HEAD
## 🧠 Overview

**SentinelAPI** is a production-ready backend system designed to **secure, monitor, and intelligently analyze API traffic**.

It combines JWT authentication, API key management, rate limiting, IP blocking, usage analytics, and a **full Machine Learning pipeline** that detects anomalous behavior, clusters IPs by behavior type, and scores risk in real-time.

> 👉 Goal: Build a **secure, scalable, and ML-powered API protection system** — portfolio-grade, interview-ready.

---

## 🌍 Problem Statement

Modern APIs face critical challenges:

- Unauthorized access and credential attacks
- API abuse, request flooding, and scraping bots
- No visibility into traffic patterns or suspicious behavior
- Reactive security instead of proactive intelligence

### 💥 Real-World Impact

- Systems become vulnerable to brute-force and DDoS attacks
- Increased server load and downtime
- No insights into API usage patterns
- Security risks go undetected until it's too late

---

## 🎯 Objectives

- Secure API access using JWT tokens and API keys
- Monitor all API traffic with request logging
- Detect and auto-block suspicious IPs
- Prevent abuse using per-key rate limiting
- Provide analytics for usage insights
- **Score IP risk using trained ML models in real-time**

---

## 🏗️ System Architecture

```text
         ┌──────────────────────────────────┐
         │           CLIENT LAYER           │
         │    Web App | Mobile | Services   │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │       AUTHENTICATION LAYER       │
         │   JWT Bearer Token Verification  │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │         SECURITY ENGINE          │
         │  API Key Validation | Rate Limit │
         │  IP Blocking | Anomaly Detection │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │        ML INTELLIGENCE LAYER     │
         │  Isolation Forest (Anomaly)      │
         │  K-Means (Behavior Clustering)   │
         │  Logistic Regression (Risk Score)│
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │          ANALYTICS LAYER         │
         │    Logs | Metrics | Insights     │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │           DATA LAYER             │
         │  Users | API Keys | Request Logs │
         │  Rate Limits | Blocked IPs       │
         └──────────────────────────────────┘
=======
## 🧠 Overview  

**SentinelAPI** is a backend system designed to **secure, monitor, and analyze API traffic** in modern applications.  

It combines authentication, request tracking, and security mechanisms to protect APIs from abuse and provide real-time insights into usage patterns.  

👉 Goal: Build a **secure, scalable, and intelligent API protection system**

---

## 🌍 Problem Statement  

Modern APIs face critical challenges:  

- Unauthorized access  
- API abuse and request flooding  
- Lack of monitoring and visibility  
- Difficulty detecting suspicious behavior  

### 💥 Real-World Impact  

- Systems become vulnerable to attacks  
- Increased server load and downtime  
- No insights into API usage patterns  
- Security risks in production systems  

---

## 🎯 Objectives  

- Secure API access using authentication and API keys  
- Monitor API traffic and user activity  
- Detect suspicious and abnormal behavior  
- Prevent abuse using rate limiting  
- Provide analytics for better decision-making  

---

## 🏗️ System Architecture  

```text
        ┌──────────────────────────┐
        │       CLIENT LAYER       │
        │  Web | Mobile | Services │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │   AUTHENTICATION LAYER   │
        │   JWT | API Key System   │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │    SECURITY ENGINE       │
        │ Rate Limit | IP Block    │
        │ Anomaly Detection        │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │     ANALYTICS LAYER      │
        │ Logs | Metrics | Insights│
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │       DATA LAYER         │
        │ Users | Keys | Requests  │
        └──────────────────────────┘
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
```

---

<<<<<<< HEAD
## 🔐 Core Features

### Auth & Access Control
- JWT-based user authentication (register + login)
- API key generation with scopes and usage limits
- Token expiry and secure password hashing (pbkdf2_sha256)

### Security Engine
- Per-key rate limiting with configurable time windows
- Automatic IP blocking on request flood detection (>100 req/min)
- Manual IP block/unblock endpoints

### Analytics
- Request count grouped by API key
- Top 5 most-hit endpoints
- Abuse detection — keys that exceeded their usage limit

### 🤖 Machine Learning Pipeline
- **Isolation Forest** — detects anomalous IPs (outlier detection)
- **K-Means Clustering** — classifies IPs into behavioral profiles
- **Logistic Regression** — scores risk probability (0.0 → 1.0)
- Ensemble output: anomaly flag + cluster label + risk tier + recommendation

---

## 🤖 ML Intelligence Layer

### Training Pipeline (offline)

```
data_generator.py   →   100k rows of synthetic API traffic
        ↓
features.py         →   Aggregate per-IP behavioral features
        ↓
train.py            →   Train 3 models → save as .pkl files
        ↓
evaluate.py         →   Metrics, confusion matrix, feature importance plots
```

### Inference (live, via API)

Send 6 IP behavioral features → get back full risk assessment:

| Feature | Description |
|---|---|
| `requests_per_min` | Average request rate |
| `endpoint_variety` | Number of unique endpoints accessed |
| `error_rate` | Fraction of 4xx/5xx responses (0.0–1.0) |
| `avg_time_between_reqs` | Seconds between requests |
| `single_endpoint_ratio` | Fraction of traffic to single endpoint |
| `user_agent_variety` | Number of distinct user agents |

### Risk Tiers

| Tier | Probability | Action |
|---|---|---|
| `SAFE` | < 0.3 | Allow — normal usage |
| `MONITOR` | 0.3 – 0.7 | Rate-limit + watch |
| `BLOCK` | ≥ 0.7 | Block immediately |

### Behavioral Clusters

| Cluster | Profile | Pattern |
|---|---|---|
| `normal` | Legitimate User | Low rate, varied endpoints, few errors |
| `bruteforce` | Brute-Force Attacker | Hammering `/auth/login` with 401s |
| `scraper` | Scraper Bot | Many endpoints, medium-high rate |
| `credential_stuffing` | Credential Stuffer | Auth bursts, rotating user agents |

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **Database** | PostgreSQL, SQLAlchemy ORM, Alembic |
| **Auth** | JWT (python-jose), Passlib (pbkdf2_sha256) |
| **Validation** | Pydantic v2, pydantic-settings |
| **ML** | scikit-learn, NumPy, Pandas, joblib |
| **Visualization** | Matplotlib, Seaborn |
| **Testing** | Pytest, HTTPX |
| **Config** | python-dotenv, `.env` file |

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login → get JWT token |

### API Keys
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api-keys/` | Create a new API key |
| `GET` | `/api-keys/` | List all API keys |
| `DELETE` | `/api-keys/{id}` | Delete an API key |

### Security
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/security/block-ip` | Block an IP address |
| `GET` | `/security/blocked-ips` | List all blocked IPs |
| `DELETE` | `/security/unblock-ip/{id}` | Unblock an IP |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics/requests` | Request counts by API key |
| `GET` | `/analytics/top-endpoints` | Top 5 most-hit endpoints |
| `GET` | `/analytics/abuse-detection` | Keys exceeding usage limit |

### Machine Learning
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/ml/status` | Are models loaded? Feature list? |
| `POST` | `/ml/reload` | Reload .pkl models from disk |
| `POST` | `/ml/score` | Full risk score for an IP |
| `POST` | `/ml/cluster` | Behavioral profile for an IP |

---

## 🧪 Example Usage

### 1. Register a User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "alice",
  "email": "alice@example.com",
  "password": "securepassword"
}
```

### 2. Login → Get JWT
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=alice&password=securepassword
```
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

### 3. Score an IP with ML
```http
POST /ml/score
Authorization: Bearer <token>
X-API-Key: <your-api-key>
Content-Type: application/json

{
  "requests_per_min": 3.5,
  "endpoint_variety": 2,
  "error_rate": 0.85,
  "avg_time_between_reqs": 15.0,
  "single_endpoint_ratio": 0.90,
  "user_agent_variety": 1
}
```
```json
{
  "anomaly": true,
  "anomaly_score": -0.42,
  "cluster_id": 1,
  "cluster_label": "bruteforce",
  "risk_probability": 0.91,
  "risk_tier": "BLOCK",
  "recommendation": "HIGH RISK — Recommend immediate blocking."
=======
## 🔐 Core Features  

- JWT-based user authentication  
- API key generation and management  
- Rate limiting for abuse prevention  
- Request logging and analytics  
- Suspicious activity detection  
- IP blocking for malicious clients  

---

## 🧠 Security Engine  

### ⚡ Rate Limiting  
Prevents excessive requests and protects the system from abuse  

### 🚫 IP Blocking  
Blocks malicious or suspicious IP addresses  

### 🔍 Anomaly Detection  
Detects unusual patterns in API usage  

---

## 📊 Analytics System  

- Tracks API request activity  
- Identifies high-traffic endpoints  
- Detects abnormal usage behavior  
- Provides insights for system monitoring  

---

## 🔁 System Workflow  

```text
Client Request → Authentication → API Key Validation → Security Checks → Request Logging → Response → Analytics
```

---

## ⚙️ Tech Stack  

### Backend  
- Python  
- FastAPI  
- Uvicorn  

### Database  
- PostgreSQL  
- SQLAlchemy  
- Alembic  

### Security  
- JWT (python-jose)  
- Passlib (password hashing)  

### Validation  
- Pydantic  

---

## 🧪 Example API  

### Register User  

```http
POST /auth/register
```

```json
{
  "username": "test",
  "email": "test@email.com",
  "password": "123456"
}
```

---

### Login  

```http
POST /auth/login
```

```json
{
  "access_token": "your_token_here",
  "token_type": "bearer"
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
}
```

---

<<<<<<< HEAD
## ▶️ How to Run

### 1. Clone & Setup
```bash
git clone https://github.com/your-username/sentinel-api.git
cd sentinel-api

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and secret key
```

### 3. Train the ML Models (first time only)
```bash
python -m ml.data_generator   # generate synthetic data
python -m ml.train             # train and save models
python -m ml.evaluate          # view metrics and plots
```

### 4. Start the Server
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Open Swagger UI
```
http://127.0.0.1:8000/docs
=======
## ▶️ How to Run  

```bash
# Clone repository
git clone https://github.com/your-username/sentinel-api.git

# Navigate
cd sentinel-api

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8001
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
```

---

<<<<<<< HEAD
## 📂 Project Structure

```text
sentinel-api-main/
│
├── .env                        ← local secrets (gitignored)
├── .env.example                ← template for other devs
├── .gitignore
├── requirements.txt
│
├── app/
│   ├── main.py                 ← FastAPI app, middleware, routers
│   ├── config.py               ← centralized settings (reads .env)
│   ├── database.py             ← SQLAlchemy engine + session
│   │
│   ├── models/                 ← DB table definitions
│   │   ├── user.py
│   │   ├── api_key.py
│   │   ├── request_log.py
│   │   ├── rate_limit.py
│   │   └── blocked_ip.py
│   │
│   ├── schemas/                ← Pydantic request/response models
│   │   ├── user_schema.py
│   │   ├── api_key_schema.py
│   │   └── ...
│   │
│   ├── routers/                ← API endpoints
│   │   ├── auth_router.py
│   │   ├── api_keys_router.py
│   │   ├── security_router.py
│   │   ├── analytics_router.py
│   │   └── ml.py
│   │
│   ├── services/               ← business logic
│   │   ├── auth_service.py     ← JWT + password hashing
│   │   ├── security_engine.py  ← auto-block + anomaly detection
│   │   ├── rate_limiter.py     ← per-key rate limiting
│   │   ├── analytics_service.py
│   │   ├── api_key_service.py
│   │   ├── email_service.py
│   │   └── ml_service.py       ← bridge to ML models
│   │
│   ├── middleware/
│   │   ├── auth_middleware.py        ← JWT validation
│   │   └── rate_limit_middleware.py  ← API key + rate limit
│   │
│   └── tests/
│       ├── test_auth.py
│       ├── test_api_keys.py
│       ├── test_rate_limit.py
│       └── test_security_engine.py
│
├── ml/
│   ├── data_generator.py       ← synthetic training data
│   ├── features.py             ← feature engineering
│   ├── train.py                ← model training
│   ├── evaluate.py             ← metrics + plots
│   ├── predict.py              ← live inference engine
│   │
│   ├── data/
│   │   ├── synthetic_requests.csv
│   │   └── ip_features.csv
│   │
│   ├── models/                 ← trained model files
│   │   ├── isolation_forest.pkl
│   │   ├── kmeans.pkl
│   │   ├── logistic_regression.pkl
│   │   ├── scaler.pkl
│   │   └── cluster_map.pkl
│   │
│   └── notebooks/plots/        ← evaluation charts
│       ├── confusion_matrix.png
│       ├── feature_importance.png
│       ├── risk_distribution.png
│       └── cluster_visualization.png
│
└── alembic/                    ← DB migrations
=======
## 📂 Project Structure  

```text
api_fortress/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── middleware/
│
├── alembic/
├── alembic.ini
└── README.md
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
```

---

<<<<<<< HEAD
## 🔥 What Makes This Project Stand Out

This is **not** just a CRUD API. It is a full **security intelligence platform**:

- ✅ Real ML models trained on behavioral data — not just rule-based detection
- ✅ Ensemble of 3 complementary models (anomaly + clustering + risk scoring)
- ✅ Clean layered architecture (middleware → router → service → model)
- ✅ Production-ready patterns: env config, ORM, Pydantic schemas, JWT auth
- ✅ End-to-end pipeline: data generation → training → evaluation → live inference

---

## 🤝 Contribution

1. Fork the repository
2. Create a new branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Submit a pull request

---

## 📜 License

MIT License

---

## 🧠 Final Thought

> *"Don't wait for an attack to understand your traffic. Let the models tell you first."*

---

⭐ If you find this project useful, give it a star and support the journey 🚀
=======
## 🔥 Unique Value Proposition  

👉 This is not just an API backend.  

It is a **Security & Monitoring System** that:  

- Protects APIs from abuse  
- Tracks and analyzes traffic  
- Detects suspicious behavior  
- Demonstrates real-world backend security concepts  

---

## 🚀 Future Improvements  

- Advanced anomaly detection using machine learning  
- Real-time monitoring dashboard  
- API usage visualization  
- Distributed rate limiting (Redis)  
- Docker & cloud deployment  

---

## 🤝 Contribution  

1. Fork the repository  
2. Create a new branch  
3. Commit changes  
4. Submit a pull request  

---

## 📜 License  

MIT License  

---

## 🧠 Final Thought  

> “Secure your APIs before scaling them.”  

---

## ⭐ Support  

If you like this project, give it a star ⭐ and support the journey 🚀  
>>>>>>> 36b22f616c006a8fae6fd7833e030d6d32b07ede
