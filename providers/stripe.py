from uuid import uuid4
from base import ChargeResponse, ChargeRequest, PaymentProvider
import asyncio
import random
from datetime import datetime, timezone


class StripeProvider(PaymentProvider):
    name = "stripe"

    async def charge(self, req: ChargeRequest) -> ChargeResponse:
        # latency
        await asyncio.sleep(random.uniform(0.2, 0.5))

        # 70% success rate
        success = random.random() > 0.70
        return ChargeResponse(
            status="success" if success else "failed",
            provider=self.name,
            provider_id=uuid4().hex[:10],
            amount=req.amount,
            currency=req.currency,
            processed_at=datetime.now(timezone.utc).isoformat()
        )

