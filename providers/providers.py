
from fastapi import FastAPI, APIRouter, HTTPException

from adyen import AdyenProvider
from base import ChargeRequest, ChargeResponse
from paypal import PayPalProvider
from stripe import StripeProvider

app = FastAPI()
router = APIRouter()

PROVIDERS = {
    "paypay": PayPalProvider,
    "stripe": StripeProvider,
    "adyen": AdyenProvider,
}

@router.post("/charges/{provider}", response_model=ChargeResponse)
async def charge(provider: str, req: ChargeRequest):
    provider_cls = PROVIDERS.get(provider)

    if not provider_cls:
        raise HTTPException(status_code=404, detail="Provider not found")

    instance = provider_cls()
    return await instance.charge(req)

app.include_router(router)