from sqlalchemy.ext.asyncio import AsyncSession
from router.db.migrations.schemas.payments import Transaction, RoutingDecisions
from router.router import RouterResponse


async def create_routing_decision(
        req: RouterResponse,
        transaction: Transaction,
        db: AsyncSession,
):
    # create new router decision
    router = RoutingDecisions(
        transaction_id=transaction.id,
        provider_chosen=req.provider,
        reason=req.reason,
        attempted_providers=req.attempted_providers,
    )
    db.add(router)
    await db.flush()

    return router
