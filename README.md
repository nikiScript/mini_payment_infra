

## Mini Payment Infrastructure

### Overview

A modular payment processing system built with a microservices architecture.
It simulates how real-world payment providers (e.g. Stripe, Adyen) handle:

* Payment authorization
* Fraud detection
* Smart routing between providers
* Post-processing reconciliation

The system is composed of independent services communicating over HTTP, backed by a shared PostgreSQL database with schema separation.

---

### Motivation

This project was built to explore what actually happens **after** a payment request hits a system:

* How do you decide which provider to use?
* What happens when providers fail?
* How do you detect fraud before money moves?
* How do you verify nothing broke afterward?

It was designed as a foundation for experimenting with:

* Fraud detection (rule-based + scoring)
* Reconciliation workers
* Provider reliability modelling
* System boundaries and service ownership

---

### Architecture

```
Client
  ↓
Gateway (auth + entry point)
  ↓
Fraud Service (risk scoring)
  ↓
Router (decision engine)
  ↓
Providers (mock external services)
  ↓
PostgreSQL (state storage)

Worker (async)
  ↳ reconciliation against providers
```

---

### Services

#### Gateway

* Entry point for all requests
* Handles API key authentication
* Forwards valid requests to fraud service

#### Fraud Service

* Evaluates transaction risk before processing
* Combines:

  * Hard rules (instant block)
  * Soft scoring (risk-based decisions)
* Reads from `payments.transactions` for velocity + behaviour analysis

#### Router

* Core decision engine
* Selects provider based on:

  * Success rate
  * Latency
  * Cost
* Implements fallback logic if providers fail

#### Providers

Mock payment processors simulating real-world behaviour:

* Random success/failure
* Variable latency
* Simple `/charge` API

#### Reconciliation Worker

* Runs periodically
* Fetches settlements from providers
* Compares with internal transaction records
* Detects:

  * Missing transactions
  * Status mismatches
  * Amount discrepancies

#### Database

Single PostgreSQL instance with separated schemas:

* `merchants` → gateway-owned
* `payments` → router-owned

Each service maintains its own migration history.

---

### Features

* API key authentication
* Multi-provider routing with fallback
* Rule-based + score-based fraud detection
* Provider performance tracking
* Reconciliation worker for consistency checks
* Schema-isolated database design

---

### Installation

```bash
git clone <repo>
cd <repo>
cp .env.example .env
docker compose up --build
```

---

### Usage

#### 1. Register a merchant

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"name": "test_merchant"}'
```

Returns:
> Note: This is the only time api_key will be returned unhashed.
> Make sure to copy it for future usage.
```json
{
  "merchant_id": "...",
  "api_key": "..."
}
```

---

#### 2. Make a payment

```bash
curl -X POST http://localhost:8000/payments \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100,
    "currency": "EUR",
    "country": "NL"
  }'
```

---

### Payment Flow

```
Client → Gateway
        → Fraud check
            → blocked | allowed
        → Router
            → choose provider
            → fallback if needed
        → Provider
        → Response returned
```

---

### Fraud Detection

Fraud evaluation is split into two layers:

#### Hard Rules (instant block)

* High velocity (transactions in short time)
* Excessive daily activity
* Repeated high-value transactions
* Geographic anomalies

#### Scoring Model

Weighted signals:

* Transaction velocity
* High-value frequency
* Geo mismatches
* Suspicious round amounts

Thresholds:

* High score → blocked
* Medium → flagged for review
* Low → allowed

---

### Reconciliation

The worker continuously validates system integrity:

* Pulls settlement data from providers
* Compares against internal transactions
* Flags inconsistencies:

  * Missing transactions
  * Status mismatches
  * Amount mismatches

Runs automatically every 60 seconds.

---

### Example Output (Worker Logs)

```
[WORKER]: Starting reconciliation run
[WORKER]: Fetching settlements for stripe
[WORKER]: STATUS MISMATCH tx_123
[WORKER]: AMOUNT MISMATCH tx_456
[WORKER]: RUN COMPLETE - checked 42 matched=38 mismatched=3 missing=1
```

---

### Future Improvements

* Idempotency handling
* Async event-driven architecture (Kafka / queues)
* Machine learning fraud models
* Auto-repair mechanisms for mismatches
* Rate limiting + abuse protection


