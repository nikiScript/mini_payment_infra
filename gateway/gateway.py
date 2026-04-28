from fastapi import FastAPI
from payments import router as payments_router
from registers import router as registers_router


app = FastAPI()

app.include_router(payments_router)
app.include_router(registers_router)