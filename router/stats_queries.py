from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.migrations.schemas.payments import ProviderStats

# get stats
async def query_stats(db: AsyncSession):

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

# update avg latency and rolling success rate
async def update_provider_stats(
        provider_name: str,
        success: bool,
        latency_ms: float,
        db: AsyncSession,
):

    result = await db.execute(
        select(ProviderStats)
        .where(ProviderStats.provider_name == provider_name)
    )
    stats = result.scalar_one_or_none()
    # if provider is not seeded, skip
    if stats is None:
        return

    stats.avg_latency_ms = (stats.avg_latency_ms * 0.9) + (latency_ms * 0.1)
    stats.success_rate = (stats.success_rate * 0.9) + (1 if success else 0) * 0.1

    await db.flush()