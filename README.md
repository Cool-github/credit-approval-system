# 🚀 Credit Approval System – Backend Assignment

A production-grade backend system built with Django, Django REST Framework, PostgreSQL, Celery, and Docker to process customer credit approvals, loan eligibility checks, and loan management based on historical data ingestion.

---

## 📌 Project Overview

This system:

- Ingests historical customer and loan data from Excel files using background workers.
- Calculates credit scores based on past loan behavior.
- Evaluates loan eligibility based on defined business rules.
- Provides REST APIs to register customers, check eligibility, create loans, and view loans.
- Fully containerized using Docker & Docker Compose.
- Includes Swagger API documentation for easy testing.

---

## ⚙️ Tech Stack

| Component | Version |
|------------|---------|
| Python | 3.10 |
| Django | 4.2 |
| Django REST Framework | 3.14 |
| PostgreSQL | 15 |
| Redis | 7 |
| Celery | 5.3 |
| Pandas | 2.x |
| Docker | Latest |
| Gunicorn | 21 |
| drf-spectacular (Swagger) | 0.27 |

---

## 🏗️ Architecture Summary

```
credit-approval-system/
│
├── apps/
│   ├── customers      → Customer model
│   ├── loans          → Loan model
│   ├── ingestion     → Excel ingestion with Celery
│   └── api           → REST API endpoints
│
├── services/         → Business logic layer
│   ├── credit_score.py
│   ├── eligibility.py
│   ├── emi_calculator.py
│   └── limit_calculator.py
│
├── config/           → Django project settings
├── tests/            → Unit & API tests
├── data/             → Excel input files
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 📂 Data Ingestion

On startup, the system ingests:

- `data/customer_data.xlsx`
- `data/loan_data.xlsx`

Excel column names are automatically mapped to database fields.

Ingestion runs asynchronously using **Celery background workers**.

### Manually trigger ingestion

```bash
docker exec -it credit_api python manage.py ingest_data
```

---

## 🚀 Running the Project

### 1️⃣ Clone the repository

```bash
git clone <your-github-repo-url>
cd credit-approval-system
```

---

### 2️⃣ Place Excel files

```
data/
├── customer_data.xlsx
└── loan_data.xlsx
```

---

### 3️⃣ Create `.env` file

```
DEBUG=True
SECRET_KEY=dev-secret-key

DB_NAME=creditdb
DB_USER=credituser
DB_PASSWORD=creditpass
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
```

---

### 4️⃣ Build & Run containers

```bash
docker-compose up --build
```

---

### 5️⃣ Run database migrations

```bash
docker exec -it credit_api python manage.py migrate
```

---

### 6️⃣ Trigger Excel ingestion

```bash
docker exec -it credit_api python manage.py ingest_data
```

---

✅ System is now fully ready.

---

## 📖 Swagger API Documentation

Interactive API docs available at:

```
http://localhost:8000/docs/
```

All POST endpoints include pre-filled example request bodies.

---

## 🔗 API Endpoints

Base URL:

```
http://localhost:8000
```

---

### ✅ 1) Register Customer

**POST** `/register`

#### Request Body

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 28,
  "monthly_income": 50000,
  "phone_number": "9999999999"
}
```

#### Response

```json
{
  "customer_id": 301,
  "name": "John Doe",
  "age": 28,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": "9999999999"
}
```

---

### ✅ 2) Check Loan Eligibility

**POST** `/check-eligibility`

#### Request Body

```json
{
  "customer_id": 301,
  "loan_amount": 500000,
  "interest_rate": 10,
  "tenure": 24
}
```

#### Response

```json
{
  "customer_id": 301,
  "approval": true,
  "interest_rate": 10,
  "corrected_interest_rate": 12,
  "tenure": 24,
  "monthly_installment": 23536.22
}
```

---

### ✅ 3) Create Loan

**POST** `/create-loan`

#### Request Body

```json
{
  "customer_id": 301,
  "loan_amount": 500000,
  "interest_rate": 10,
  "tenure": 24
}
```

#### Approved Response

```json
{
  "loan_id": 783,
  "customer_id": 301,
  "loan_approved": true,
  "message": "Loan approved",
  "monthly_installment": 23536.22
}
```

#### Rejected Response

```json
{
  "loan_id": null,
  "customer_id": 301,
  "loan_approved": false,
  "message": "Low credit score",
  "monthly_installment": 0
}
```

---

### ✅ 4) View Single Loan

**GET** `/view-loan/<loan_id>`

#### Example

```
GET /view-loan/783
```

#### Response

```json
{
  "loan_id": 783,
  "customer": {
    "id": 301,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "9999999999",
    "age": 28
  },
  "loan_amount": 500000,
  "interest_rate": 12,
  "monthly_installment": 23536.22,
  "tenure": 24
}
```

---

### ✅ 5) View All Loans of Customer

**GET** `/view-loans/<customer_id>`

#### Example

```
GET /view-loans/301
```

#### Response

```json
[
  {
    "loan_id": 783,
    "loan_amount": 500000,
    "interest_rate": 12,
    "monthly_installment": 23536.22,
    "repayments_left": 24
  }
]
```

---

## 🧪 Running Tests

```bash
docker exec -it credit_api python manage.py test tests
```

---

## 📦 One Command Full Setup

After cloning and adding Excel files:

```bash
docker-compose up --build
docker exec -it credit_api python manage.py migrate
docker exec -it credit_api python manage.py ingest_data
```

---

## 📝 Notes for Evaluator

- Excel ingestion runs asynchronously using Celery.
- Column name mismatches handled during ingestion.
- Credit score & eligibility logic implemented in isolated service layer.
- PostgreSQL used as primary database.
- Fully Dockerized environment.
- Swagger UI available for easy API testing.

---
