import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from db.migrations.schemas.payments import ProviderStats, Base

engine = create_engine(os.environ["DB_URL_SYNC_LOCAL"])

SEED_STATS = [
    {"provider_name": "stripe",  "success_rate": 0.97, "avg_latency_ms": 250, "fee_percentage": 0.029},
    {"provider_name": "paypal",  "success_rate": 0.85, "avg_latency_ms": 800, "fee_percentage": 0.035},
    {"provider_name": "adyen",   "success_rate": 0.95, "avg_latency_ms": 400, "fee_percentage": 0.025},
]

with Session(engine) as session:
    for s in SEED_STATS:
        exists = session.query(ProviderStats).filter_by(provider_name=s["provider_name"]).first()
        if not exists:
            session.add(ProviderStats(**s))
            print(f"Seeded {s['provider_name']}")
        else:
            print(f"Skipped {s['provider_name']} — already exists")
    session.commit()
    print("Done")