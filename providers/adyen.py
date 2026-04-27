from uuid import uuid4
from base import ChargeResponse, ChargeRequest, PaymentProvider
import asyncio
import random
from datetime import datetime, timezone


class AdyenProvider(PaymentProvider):
    name = "adyen"

    async def charge(self, req: ChargeRequest) -> ChargeResponse:
        # latency
        await asyncio.sleep(random.uniform(0.2, 0.3))

        # 95% success rate
        success = random.random() > 0.05
        return ChargeResponse(
            status="success" if success else "failed",
            provider=self.name,
            provider_id=uuid4().hex[:10],
            amount=req.amount,
            currency=req.currency,
            processed_at=datetime.now(timezone.utc).isoformat()
        )

