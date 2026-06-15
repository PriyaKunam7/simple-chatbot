# app/settlement.py

import time

from app.config import get_commission_rate
from app.database import create_settlement, update_order_status
from app.events import publish_settlement_completed


def process_settlement(order_id: int, seller_id: str, amount: float):
    """
    Simulate background settlement processing
    (similar to a Celery worker handling payouts)
    """

    print("\n" + "=" * 60)
    print(f"⚙️ CELERY WORKER: Processing settlement for Order #{order_id}")
    print("=" * 60)

    try:
        # Get commission configuration (simulating MongoDB config lookup)
        commission_rate = get_commission_rate(seller_id)

        print(f"📋 CONFIG SERVICE (MongoDB): Commission rate for {seller_id}: {commission_rate * 100:.2f}%")

        commission = round(amount * commission_rate, 2)
        settlement_amount = round(amount - commission, 2)

        print("\n💵 SETTLEMENT CALCULATION")
        print(f"   Original Amount: ${amount:.2f}")
        print(f"   Commission ({commission_rate * 100:.2f}%): ${commission:.2f}")
        print(f"   Settlement Amount: ${settlement_amount:.2f}")

        # Simulate bank payout processing
        print("\n⏳ BANK API CALL: Simulating payout processing (2 seconds)...")
        time.sleep(2)

        # Save settlement record
        settlement = create_settlement(
            order_id,
            seller_id,
            amount,
            commission,
            settlement_amount
        )

        # Update order status
        update_order_status(order_id, "settled")

        # Publish event
        publish_settlement_completed(
            settlement.id,
            order_id,
            settlement_amount
        )

        print("\n✅ CELERY WORKER: Settlement completed successfully!")
        print("=" * 60 + "\n")

        return settlement

    except Exception as e:

        print("\n❌ CELERY WORKER: Settlement failed!")
        print(f"Reason: {str(e)}")
        print("=" * 60 + "\n")

        raise