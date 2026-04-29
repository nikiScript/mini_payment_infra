
from sqlalchemy.ext.asyncio import AsyncSession
from router.db.migrations.schemas.payments import Transaction
from pydantic import BaseModel

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    country: str


async def register_transaction(
        merchant_id: str,
        payment: PaymentRequest,
        db: AsyncSession
):

    # create new transaction
    transaction = Transaction(
        merchant_id=merchant_id,
        amount=payment.amount,
        currency=payment.currency,
        country=payment.country,
        status="pending",
    )
    db.add(transaction)
    await db.flush()

    # send to router query and to score calculation
    return transaction