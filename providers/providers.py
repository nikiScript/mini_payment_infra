from fastapi import FastAPI, HTTPException

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

@app.post("/charges/{provider}", response_model=ChargeResponse)
async def charge(provider: str, req: ChargeRequest):
    provider_cls = PROVIDERS.get(provider)

    if not provider_cls:
        raise HTTPException(status_code=404, detail="Provider not found")

    instance = provider_cls()
    return await instance.charge(req)
