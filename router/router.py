import enum
from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.payments import PaymentRequest
from db.queries.routing_queries import create_routing_decision
from db.queries.stats_queries import query_stats
from db.queries.transaction_queries import register_transaction


class Provider(enum.Enum):
    stripe = "stripe_mock"
    paypal = "paypal_mock"
    adyen = "adyen_mock"

class RouterResponse(BaseModel):
    provider: Provider
    reason: str
    attempted_providers: List[str]



async def router(
        merchant_id: str,
        payment: PaymentRequest,
        db: AsyncSession
):

    tx = await register_transaction(merchant_id, payment, db)

    stats = await query_stats(db)

    router_response = choose_provider(payment, stats)

    await create_routing_decision(router_response, tx, db)

    await db.commit()

    return tx


def choose_provider(payment, stats):
    pass

from operator import itemgetter

def choose_provider(payment, stats):
    scored = []

    for provider_name, s in stats.items():
        score = score_provider(s)

        scored.append({
            "provider": provider_name,
            "score": score
        })

    # best first
    scored.sort(key=itemgetter("score"), reverse=True)

    best = scored[0]
    second = scored[1:]

    return RouterResponse(
        provider=best["provider"],
        reason=f"highest score: {best['score']:.3f}",
        attempted_providers=[p["provider"] for p in second]
    )


def score_provider(stats_entry):
    success = stats_entry["success_rate"]            # already 0–1
    latency = 1 / (1 + stats_entry["avg_latency_ms"] / 100)
    cost = 1 - stats_entry["fee_percentage"]         # lower fee = better

    # weighted model
    return (
        0.6 * success +
        0.25 * latency +
        0.15 * cost
    )

def normalize_latency(latency_ms: float) -> float:
    return 1 / (1 + latency_ms / 100)

def choose_provider(payment: PaymentRequest, stats: dict) -> RouterResponse:
    best_provider = None
    best_score = float("-inf")
    attempted = []

    for provider, data in stats.items():
        attempted.append(provider)

        score = (
            data["success_rate"] * 0.6
            - (data["avg_latency_ms"] / 1000) * 0.2
            - data["fee_percentage"] * 0.2
        )

        if score > best_score:
            best_score = score
            best_provider = provider

    return RouterResponse(
        provider=best_provider,
        reason=f"highest score ({best_score:.3f})",
        attempted_providers=attempted,
    )

def choose_provider(payment, stats):
    best_provider = None
    best_score = -1
    attempted = []

    for provider, stat in stats.items():
        success = stat["success_rate"]
        latency = stat["avg_latency_ms"]
        fee = stat["fee_percentage"]

        # avoid division by zero
        latency_score = 1 / latency if latency else 0
        fee_score = 1 / fee if fee else 0

        score = (
            success * 0.6 +
            latency_score * 0.3 +
            fee_score * 0.1
        )

        attempted.append(provider)

        if score > best_score:
            best_score = score
            best_provider = provider

    return RouterResponse(
        provider=best_provider,
        reason=f"highest score: {best_score:.4f}",
        attempted_providers=attempted
    )