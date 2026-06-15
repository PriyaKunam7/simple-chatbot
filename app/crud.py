from typing import Optional
from fastapi import HTTPException

from app.database import (
    create_order as db_create_order,
    get_order as db_get_order,
    get_all_orders as db_get_all_orders,
    update_order_status as db_update_order_status,
    delete_order as db_delete_order,
    cache_order,
    get_cached_order,
    clear_cache,
    get_all_settlements,
    get_analytics as db_get_analytics
)

from app.config import validate_seller
from app.events import publish_order_created, publish_order_updated
from app.settlement import process_settlement


def create_order(product_id: str, customer_id: str, seller_id: str, amount: float) -> dict:
    """
    Create a new order and trigger settlement pipeline
    """

    if not validate_seller(seller_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid seller_id: {seller_id}"
        )

    order = db_create_order(product_id, customer_id, seller_id, amount)

    # Cache order
    cache_order(order.id, order.to_dict())

    # Publish event
    publish_order_created(order.id, seller_id, amount)

    # Process settlement
    process_settlement(order.id, seller_id, amount)

    return {
        "order_id": order.id,
        "status": "created",
        "message": "Order created and settlement processed successfully"
    }


def get_order(order_id: int) -> dict:
    """
    Retrieve order (check cache first)
    """

    cached_order = get_cached_order(order_id)
    if cached_order:
        return cached_order

    order = db_get_order(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order #{order_id} not found"
        )

    order_dict = order.to_dict()

    # Cache result
    cache_order(order_id, order_dict)

    return order_dict


def list_orders(skip: int = 0, limit: int = 10, status: Optional[str] = None) -> dict:
    """
    List orders with optional status filter
    """

    orders = db_get_all_orders(skip, limit)

    if status:
        orders = [order for order in orders if order.status == status]

    return {
        "total": len(orders),
        "orders": [order.to_dict() for order in orders]
    }


def update_order(order_id: int, new_status: str) -> dict:
    """
    Update order status
    """

    order = db_get_order(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order #{order_id} not found"
        )

    old_status = order.status

    updated = db_update_order_status(order_id, new_status)

    if not updated:
        raise HTTPException(
            status_code=500,
            detail="Failed to update order"
        )

    # Clear cache
    clear_cache(order_id)

    # Publish event
    publish_order_updated(order_id, old_status, new_status)

    return {
        "order_id": order_id,
        "old_status": old_status,
        "new_status": new_status,
        "message": "Order updated successfully"
    }


def delete_order(order_id: int) -> dict:
    """
    Cancel/Delete an order
    """

    order = db_get_order(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order #{order_id} not found"
        )

    success = db_delete_order(order_id)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete order"
        )

    # Clear cache
    clear_cache(order_id)

    return {
        "order_id": order_id,
        "message": "Order deleted successfully"
    }


def get_settlements() -> dict:
    """
    Get all settlements
    """

    settlements = get_all_settlements()

    return {
        "total": len(settlements),
        "settlements": [settlement.to_dict() for settlement in settlements]
    }


def get_analytics() -> dict:
    """
    Return analytics summary
    """

    return db_get_analytics()