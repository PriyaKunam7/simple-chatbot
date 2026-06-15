# app/events.py

import json
from typing import Dict


def publish_event(event_type: str, event_data: Dict) -> bool:
    """
    Simulate publishing an event to Kafka.
    In a real system this would send data to a Kafka topic.
    """

    print("\n📢 KAFKA EVENT")
    print(f"Topic: {event_type}")
    print("Payload:")
    print(json.dumps(event_data, indent=2))

    return True


def publish_order_created(order_id: int, seller_id: str, amount: float) -> Dict:
    """
    Event fired when a new order is created
    """

    event_data = {
        "order_id": order_id,
        "seller_id": seller_id,
        "amount": amount
    }

    publish_event("order.created", event_data)

    return event_data


def publish_order_updated(order_id: int, old_status: str, new_status: str) -> Dict:
    """
    Event fired when order status changes
    """

    event_data = {
        "order_id": order_id,
        "old_status": old_status,
        "new_status": new_status
    }

    publish_event("order.updated", event_data)

    return event_data


def publish_settlement_completed(settlement_id: int, order_id: int, amount: float) -> Dict:
    """
    Event fired when settlement is completed
    """

    event_data = {
        "settlement_id": settlement_id,
        "order_id": order_id,
        "amount": amount
    }

    publish_event("settlement.completed", event_data)

    return event_data