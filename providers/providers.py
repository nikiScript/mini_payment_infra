from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from collections import defaultdict

from Adyen import AdyenProvider
from Base import ChargeRequest, ChargeResponse
from Paypal import PayPalProvider
from Stripe import StripeProvider

app = FastAPI()

PROVIDERS = {
    "paypal": PayPalProvider,
    "stripe": StripeProvider,
    "adyen": AdyenProvider,
}

# normally settlements are persisted via a webhook
# for simplicity in memory-storage is used
settlements_store = defaultdict(list)

@app.post("/charges/{provider}", response_model=ChargeResponse)
async def charge(provider: str, transaction_id: str, req: ChargeRequest):
    provider_cls = PROVIDERS.get(provider)
    if not provider_cls:
        raise HTTPException(status_code=404, detail="Provider not found")

    instance = provider_cls()
    resp = await instance.charge(req)

    settlements_store[provider].append({
        "transaction_id": transaction_id,
        "amount": resp.amount,
        "currency": resp.currency,
        "status": resp.status,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    })

    return resp

@app.get("/settlements/{provider}")
async def get_settlements(provider: str):
    if provider not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")

    return {
        "provider": provider,
        "settlements": settlements_store[provider]
    }