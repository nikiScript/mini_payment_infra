import asyncio
import os
import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal

import sys
sys.stdout.reconfigure(line_buffering=True)
PROVIDERS = ["adyen", "stripe", "paypal"]
PROVIDERS_URL = os.environ.get("PROVIDERS_URL", "http://providers:8002")


async def fetch_settlements(provider: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{PROVIDERS_URL}/settlements/{provider}",
                timeout=5,
            )
            data = resp.json()
            return data.get("settlements", [])
        except Exception as e:
            print(f"[WORKER]: Failed to fetch settlements for {provider}: {e}")
            return []

async def reconcile(db: AsyncSession):
    print("[WORKER]: Starting reconciliation run")

    total_checked = 0
    matched = 0
    mismatched = 0
    missing = 0
    all_settlement_ids = set()

    # checking every provider is not recommended
    # but for this demo it will suffice
    for provider in PROVIDERS:
        print(f"[WORKER]: Fetching settlements for {provider}")
        settlements = await fetch_settlements(provider)

        # compare against settlements first
        for settlement in settlements:
            transaction_id = settlement.get("transaction_id")
            # to be used later
            all_settlement_ids.add(transaction_id)
            provider_status = settlement.get("status")
            provider_amount = settlement.get("amount")
            total_checked += 1

            # query the db for this transaction
            result = await db.execute(
                text("""
                    SELECT id, status, amount
                    FROM payments.transactions
                    WHERE id = :transaction_id
                """),
                {"transaction_id": transaction_id}
            )
            row = result.mappings().one_or_none()

            if row is None:
                missing += 1
                print(f"[WORKER]: MISSING transaction {transaction_id} from {provider}")
                continue

            our_status = row["status"]
            our_amount = row["amount"]

            # check for status mismatch
            if provider_status != our_status:
                mismatched += 1
                print(f"[WORKER]: STATUS MISMATCH {transaction_id}: ours={our_status} provider={provider_status}")
                continue

            # check amount mismatch
            if abs(our_amount - provider_amount) > 0.01:
                mismatched += 1
                print(f"[WORKER]: AMOUNT MISMATCH {transaction_id}: ours={our_amount} provider={provider_amount}")
                continue

            matched += 1

    # checking against the db next
    result = await db.execute(
        text("""
            SELECT id, status, amount
            FROM payments.transactions
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
    )
    db_transactions = result.mappings().all()

    for tx in db_transactions:
        tx_id = str(tx["id"])
        if tx_id not in all_settlement_ids:
            missing += 1
            print(f"[WORKER]: MISSING settlement for {tx_id}")

    print(f"[WORKER]: RUN COMPLETE - checked {total_checked} matched={matched} mismatched={mismatched} missing={missing}")
    return {
        "total_checked": total_checked,
        "matched": matched,
        "mismatched": mismatched,
        "missing": missing,
    }

async def run_worker():
    async with AsyncSessionLocal() as db:
        await reconcile(db)


async def main():
    print("[WORKER]: Starting reconciliation run")
    while True:
        await run_worker()
        print("[WORKER]: Sleeping for 60 seconds")
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())