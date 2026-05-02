from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# we don't have Transaction SQLAlchemy model therefore we need to use raw SQL

async def get_transactions_data(
        merchant_id: str,
        country: str,
        db: AsyncSession
):

    result = await db.execute(
        text(
            '''
            SELECT
                -- velocity
                COUNT(*) FILTER (
                    WHERE created_at > NOW() - INTERVAL '10 minutes'
                ) AS velocity_10m,
                
                -- last 24h activity
                COUNT(*) AS total_24h,
                
                -- country mismatch
                COUNT(*) FILTER (
                    WHERE country != :country
                ) As geo_mismatch,
                
                -- high value transactions
                COUNT(*) FILTER (
                    WHERE amount > 5000
                ) AS high_value_count,
                
                -- suspicious round amounts
                COUNT(*) FILTER (
                    WHERE amount % 100 = 0
                ) AS round_amount_count
                
            FROM payments.transactions
            WHERE merchant_id = :merchant_id
                AND created_at > NOW() - INTERVAL '24 hours'
            '''
        ), {
            'merchant_id': merchant_id,
            'country': country,
        }
    )

    row = result.mappings().one()

    return {
           "merchant_id": merchant_id,
            "velocity_10m": row["velocity_10m"],
            "total_24h": row["total_24h"],
            "high_value_count": row["high_value_count"],
            "geo_mismatch": row["geo_mismatch"],
            "round_amount_count": row["round_amount_count"],
        }