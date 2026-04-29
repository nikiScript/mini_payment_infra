from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from router.db.migrations.schemas.payments import ProviderStats

async def query_stats(db: AsyncSession):

    # query stats table
    result = await db.execute(
        select(ProviderStats)
    )
    stats = result.scalars().all()

    return {
        stat.provider_name: {
            "success_rate": stat.success_rate,
            "avg_latency_ms": stat.avg_latency_ms,
            "fee_percentage": stat.fee_percentage
        }
        for stat in stats
    }