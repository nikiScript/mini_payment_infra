from sqlalchemy.ext.asyncio import AsyncSession
from db.migrations.schemas.payments import Transaction, RoutingDecisions
from models import RouterResponse

# create new router decision
async def create_routing_decision(
        req: RouterResponse,
        transaction: Transaction,
        db: AsyncSession,
):
    router = RoutingDecisions(
        transaction_id=transaction.id,
        provider_chosen=req.provider.value if req.provider else None,
        reason=req.reason,
        attempted_providers=req.attempted_providers,
    )
    db.add(router)
    await db.flush()

    return router
