

## Mini Payment Infrastructure

### Overview

A modular payment orchestration system built with a microservices architecture. It simulates the infrastructure layer that sits **above** payment processors like Stripe and Adyen — deciding where to route payments, detecting fraud before money moves, and verifying consistency afterward.
The system is composed of independent services communicating over HTTP, backed by a shared PostgreSQL database with schema separation.

---


### Features

* API key authentication
* Multi-provider routing with fallback
* Rule-based + score-based fraud detection
* Provider performance tracking
* Reconciliation worker for consistency checks
* Schema-isolated database design

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

Single entry point. Validates merchant API keys against hashed values in the database. 
Calls the fraud service before forwarding to the router. Nothing else.

#### Fraud Service

Evaluates transaction risk before any money moves. 
Combines hard rules (instant block on velocity spikes or repeated high-value transactions) 
with a weighted scoring model. Reads directly from `payments.transactions` 
to perform real-time velocity and behavioural analysis using a single aggregated SQL query.

#### Router

The core decision engine. Scores each provider using a weighted model across success rate, 
latency, and fee. Picks the best provider, attempts the charge, and 
falls back to the next provider on failure. Updates rolling performance stats
after every call so routing decisions improve over time.

#### Providers

Mock payment processors (Stripe, Adyen, PayPal) with configurable success rates and
simulated latency. Each exposes a `/charge` endpoint and a `/settlements/{provider}` 
endpoint for reconciliation

#### Reconciliation Worker

runs every 60 seconds. Fetches settlement data from each provider, 
compares against internal transaction records, and reports missing transactions, 
status mismatches, and amount discrepancies.

#### Database

Single PostgreSQL instance with separated schemas:

* `merchants` → gateway-owned
* `payments` → router-owned

Each service maintains its own migration history.



---

### Installation

```bash
git clone <repo>
cd <repo>
cp .env.example .env
docker compose build
bash scripts/migrate.sh
docker compose up
```

---

### Usage

#### 1. Register a merchant

```bash
curl -X POST http://localhost:8003/register \
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
curl -X POST http://localhost:8003/payments \
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
### Router
 
#### Provider Scoring
 
The router scores each provider on every request using a weighted model:
 
```python
score = (
    0.60 * success_rate +
    0.25 * normalised_latency +
    0.15 * (1 - fee_percentage)
)
```
 
Stats update after every call using a rolling average:
 
```python
success_rate = (success_rate * 0.9) + (1.0 if success else 0.0) * 0.1
```
 
This means the router adapts over time — if a provider starts degrading, its score drops within ~10 calls and traffic shifts to better-performing alternatives automatically.

---

### Reconciliation

The worker continuously validates system integrity:

* Pulls settlement data from providers
* Compares against internal transactions
* Flags inconsistencies:

  * Missing transactions
  * Status mismatches
  * Amount mismatches

Settlement data is stored in-memory in the providers service. 
In production this would be persisted via provider webhooks or SFTP settlement files.


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


