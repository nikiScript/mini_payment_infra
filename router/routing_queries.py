import enum
from typing import Optional, List

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from db.migrations.schemas.payments import Transaction, RoutingDecisions

class Provider(enum.Enum):
    stripe = "stripe"
    paypal = "paypal"
    adyen = "adyen"

class RouterResponse(BaseModel):
    provider: Optional[Provider]
    reason: str
    attempted_providers: List[str]


# create new router decision
async def create_routing_decision(
        req: RouterResponse,
        transaction: Transaction,
        db: AsyncSession,
):
    router = RoutingDecisions(
        transaction_id=transaction.id,
        provider_chosen=req.provider.value,
        reason=req.reason,
        attempted_providers=req.attempted_providers,
    )
    db.add(router)
    await db.flush()

    return router
