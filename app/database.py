from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db_connection import SessionLocal
from app.models import Order, Settlement


# -----------------------------
# Simple in-memory cache
# (Simulating Redis)
# -----------------------------
cache: Dict[str, dict] = {}


def _get_db() -> Session:
    """Create a new database session"""
    return SessionLocal()


# =====================================================
# ORDERS
# =====================================================

def create_order(product_id: str, customer_id: str, seller_id: str, amount: float) -> Order:
    db = _get_db()

    try:
        order = Order(
            product_id=product_id,
            customer_id=customer_id,
            seller_id=seller_id,
            amount=amount,
            status="pending"
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    except SQLAlchemyError as e:
        db.rollback()
        print("❌ ORDER CREATION FAILED:", e)
        raise

    finally:
        db.close()


def get_order(order_id: int) -> Optional[Order]:
    db = _get_db()

    try:
        return db.query(Order).filter(Order.id == order_id).first()

    finally:
        db.close()


def get_all_orders(skip: int = 0, limit: int = 10) -> List[Order]:
    db = _get_db()

    try:
        return (
            db.query(Order)
            .order_by(Order.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    finally:
        db.close()


def update_order_status(order_id: int, new_status: str) -> Optional[Order]:
    db = _get_db()

    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            return None

        order.status = new_status
        db.commit()
        db.refresh(order)

        return order

    except SQLAlchemyError as e:
        db.rollback()
        print("❌ ORDER UPDATE FAILED:", e)
        raise

    finally:
        db.close()


def delete_order(order_id: int) -> bool:
    """
    HARD DELETE from PostgreSQL.

    Deletes settlements first to avoid FK constraint issues,
    then deletes the order.
    """

    db = _get_db()

    try:
        # Delete settlements linked to this order
        db.query(Settlement).filter(
            Settlement.order_id == order_id
        ).delete(synchronize_session=False)

        # Delete the order
        deleted = db.query(Order).filter(
            Order.id == order_id
        ).delete(synchronize_session=False)

        db.commit()

        return deleted > 0

    except SQLAlchemyError as e:
        db.rollback()
        print("❌ DELETE FAILED:", e)
        raise

    finally:
        db.close()


# =====================================================
# SETTLEMENTS
# =====================================================

def create_settlement(
    order_id: int,
    seller_id: str,
    original_amount: float,
    commission: float,
    settlement_amount: float,
) -> Settlement:

    db = _get_db()

    try:
        settlement = Settlement(
            order_id=order_id,
            seller_id=seller_id,
            original_amount=original_amount,
            commission=commission,
            settlement_amount=settlement_amount,
            status="completed",
        )

        db.add(settlement)
        db.commit()
        db.refresh(settlement)

        return settlement

    except SQLAlchemyError as e:
        db.rollback()
        print("❌ SETTLEMENT CREATION FAILED:", e)
        raise

    finally:
        db.close()


def get_all_settlements() -> List[Settlement]:
    db = _get_db()

    try:
        return db.query(Settlement).order_by(Settlement.id.asc()).all()

    finally:
        db.close()


# =====================================================
# CACHE (Redis Simulation)
# =====================================================

def cache_order(order_id: int, order_data: dict):
    cache[f"order:{order_id}"] = order_data


def get_cached_order(order_id: int) -> Optional[dict]:
    return cache.get(f"order:{order_id}")


def clear_cache(order_id: int):
    cache.pop(f"order:{order_id}", None)


# =====================================================
# ANALYTICS (Simulating PySpark Aggregations)
# =====================================================

def get_analytics() -> dict:
    db = _get_db()

    try:
        total_orders = db.query(func.count(Order.id)).scalar() or 0

        total_revenue = (
            db.query(func.coalesce(func.sum(Order.amount), 0))
            .scalar()
            or 0
        )

        total_settled = (
            db.query(func.coalesce(func.sum(Settlement.settlement_amount), 0))
            .scalar()
            or 0
        )

        total_commission = (
            db.query(func.coalesce(func.sum(Settlement.commission), 0))
            .scalar()
            or 0
        )

        status_rows = (
            db.query(Order.status, func.count(Order.id))
            .group_by(Order.status)
            .all()
        )

        status_breakdown = {status: int(count) for status, count in status_rows}

        seller_rows = (
            db.query(
                Order.seller_id,
                func.coalesce(func.sum(Order.amount), 0)
            )
            .group_by(Order.seller_id)
            .all()
        )

        seller_revenue = {sid: float(val) for sid, val in seller_rows}

        return {
            "overview": {
                "total_orders": int(total_orders),
                "total_revenue": round(float(total_revenue), 2),
                "total_settled": round(float(total_settled), 2),
                "total_commission": round(float(total_commission), 2),
            },
            "status_breakdown": status_breakdown,
            "seller_revenue": seller_revenue,
            "cache_size": len(cache),
        }

    finally:
        db.close()


# =====================================================
# ADMIN RESET
# =====================================================

def reset_database():
    db = _get_db()

    try:
        db.query(Settlement).delete()
        db.query(Order).delete()

        db.commit()

        cache.clear()

    except SQLAlchemyError:
        db.rollback()
        raise

    finally:
        db.close()