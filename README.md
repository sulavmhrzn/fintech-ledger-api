# 💳 Fintech Ledger API

A production-ready fintech ledger backend built with **FastAPI**, featuring multi-wallet management, KYC compliance, idempotent fund transfers, and async task processing.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + Async SQLAlchemy |
| Task Queue | Celery + Redis |
| Cache / Broker | Redis |
| Auth | JWT (Access + Refresh tokens) |
| Containerization | Docker / Docker Compose |

---

## ✨ Features

- **JWT Authentication** — Access & refresh token pair with email verification flow
- **Multi-Wallet Support** — Users can open and manage multiple wallets
- **Double-Entry Ledger** — All transactions recorded as ledger entries for auditability
- **Fund Transfers & Deposits** — Wallet-to-wallet transfers and simulated bank deposits
- **Idempotency** — Idempotency keys on mutating endpoints to prevent duplicate transactions
- **KYC Compliance** — Document upload and admin review workflow
- **Admin Controls** — Freeze wallets, ban users, review KYC documents
- **Async Celery Tasks** — Email verification sent via background worker
- **Celery Beat Scheduler** — Periodic cleanup of expired tokens

---

## 📡 API Reference

Base path: `/api/v1`

### 🔐 Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive token pair |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/verify-email` | Verify email with token |
| `POST` | `/auth/resend-verification` | Resend verification email |

### 👤 Users

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users/me` | Get current user profile |

### 💼 Wallets

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/wallets` | Open a new wallet |
| `GET` | `/wallets` | List all my wallets |

### 📒 Ledger

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/wallets/{wallet_id}/deposit` | Simulate loading funds from an external bank |
| `POST` | `/wallets/{wallet_id}/transfer` | Transfer funds to another wallet |
| `GET` | `/wallets/{wallet_id}/transactions` | View wallet transaction history |

### 📄 KYC

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/kyc/documents` | Upload a KYC document |

### 🛡️ Admin & Compliance

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/users` | List all users |
| `POST` | `/admin/users/{user_id}/toggle-active` | Ban or un-ban a user |
| `POST` | `/admin/wallets/{wallet_id}/toggle-freeze` | Freeze or unfreeze a wallet |
| `GET` | `/admin/kyc` | List KYC documents (cursor-paginated) |
| `POST` | `/admin/kyc/{document_id}/review` | Approve or reject a KYC document |

---

## ⚙️ Background Tasks

### Celery Workers
- **Email Verification** — Triggered on registration; dispatches a verification email asynchronously via a Celery task.

### Celery Beat (Scheduled)
- **Expired Token Cleanup** — Periodic job that purges expired refresh tokens from the database.

---

## 🔒 Auth & Security

- **JWT** — Short-lived access tokens paired with longer-lived refresh tokens.
- **Email Verification** — Accounts require email confirmation before full access.
- **Role-based Access** — Endpoints are guarded by user roles (User / Compliance / Admin).
- **Idempotency Keys** — Supply an `Idempotency-Key` header on deposit and transfer requests to safely retry without duplicating transactions.

---

## 🐳 Running Locally

### Prerequisites
- Docker & Docker Compose

### Steps

```bash
git clone https://github.com/sulavmhrzn/fintech-ledger-api.git
cd fintech-ledger-api

cp .env.example .env
# Fill in your environment variables

docker compose up --build
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

