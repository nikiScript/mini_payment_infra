from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Transaction SQLAlchemy model is not available therefore
# we need to use raw SQL query here
async def get_transactions_data(
        merchant_id: str,
        country: str,
        db: AsyncSession
):

    result = await db.execute(
        text(
            '''
            SELECT
            
                -- velocity 2m
                COUNT(*) FILTER (
                    WHERE created_at > NOW() - INTERVAL '2 minutes'
                ) AS velocity_2m,
            
                -- velocity 10m
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
                    WHERE amount::int % 100 = 0
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
            "velocity_2m": row["velocity_2m"],
            "total_24h": row["total_24h"],
            "high_value_count": row["high_value_count"],
            "geo_mismatch": row["geo_mismatch"],
            "round_amount_count": row["round_amount_count"],
        }

