import enum
import time
import os
import httpx
from typing import List, Optional

from fastapi import FastAPI, Depends, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

from routing_queries import create_routing_decision
from stats_queries import query_stats
from transaction_queries import register_transaction, update_transaction_status
from stats_queries import update_provider_stats
from operator import itemgetter


class PaymentRequest(BaseModel):
    amount: int
    currency: str
    country: str

class Provider(enum.Enum):
    stripe = "stripe"
    paypal = "paypal"
    adyen = "adyen"

class RouterResponse(BaseModel):
    provider: Optional[Provider]
    reason: str
    attempted_providers: List[str]

app = FastAPI()

@app.post("/router")
async def router(
        req: PaymentRequest,
        merchant_id: str = Header(...),
        db: AsyncSession = Depends(get_db)
):
    print("[ROUTER]: Transaction registered")
    tx = await register_transaction(merchant_id, req, db)
    stats = await query_stats(db)
    if not stats:
        raise Exception("No provider stats available")
    sorted_providers = sort_providers(stats)
    print("[ROUTER]: Sorted stats")

    attempted = []
    final_provider = None
    final_reason = "all providers failed"

    for p in sorted_providers:

        print(f"[ROUTER]: Trying {p['provider']}")
        provider_name = p["provider"]
        attempted.append(provider_name)
        result = await call_provider(provider_name, req)

        if result["status"] == "success":
            final_provider = Provider(provider_name)
            if len(attempted) == 1:
                final_reason = f"highest score {p['score']:.3f}"
            else:
                final_reason = f"fallback success after {len(attempted)} attempts"
            await update_transaction_status(tx.id, "success", db)
            await update_provider_stats(provider_name, True, result["latency_ms"], db)
            print(f"[ROUTER]: Success with {p["provider"]}")
            break

        await update_provider_stats(provider_name, False, result["latency_ms"], db)

    # all providers failed
    else:
        await update_transaction_status(tx.id, "failed", db)

    router_response = RouterResponse(
        provider=final_provider,
        reason=final_reason,
        attempted_providers=attempted
    )

    # final write to the RoutingDecision table
    print(f"[ROUTER]: Writing to the RoutingDecision table")
    await create_routing_decision(router_response, tx, db)
    await db.commit()

    return router_response


def sort_providers(stats):
    scored = []

    for provider_name, s in stats.items():
        score = score_providers(s)
        scored.append({"provider": provider_name, "score": score})

    # best first
    scored.sort(key=itemgetter("score"), reverse=True)
    return scored

def score_providers(stats_entry):
    success = stats_entry["success_rate"]
    # latency needs to be normalized
    latency = 1 / (1 + stats_entry["avg_latency_ms"] / 100)
    cost = 1 - stats_entry["fee_percentage"]

    # weighted model
    return (
        0.6 * success +
        0.25 * latency +
        0.15 * cost
    )

async def call_provider(
    provider_name: str,
    payment: PaymentRequest
):
    # start measuring latency
    start = time.monotonic()

    PROVIDERS_URL = os.environ.get("PROVIDERS_URL", "http://providers:8002")
    url = f"{PROVIDERS_URL}/charges/{provider_name}"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{url}",
                json={
                    "amount": payment.amount,
                    "currency": payment.currency,
                },
                timeout=5,
            )
            latency_ms = (time.monotonic() - start) * 1000
            if resp.status_code != 200:
                return {
                    "status": "failed",
                    "reason": f"http_{resp.status_code}",
                    "latency_ms": latency_ms
                }

            data = resp.json()
            data["latency_ms"] = latency_ms
            return data

        except httpx.TimeoutException:
            return {"status": "failed", "reason": "timeout", "latency_ms": 5000}
        except httpx.ConnectError:
            return {"status": "failed", "reason": "provider_unreachable", "latency_ms": 0}
        except Exception as e:
            return {"status": "failed", "reason": str(e), "latency_ms": 0}

