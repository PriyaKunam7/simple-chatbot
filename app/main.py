from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from sqlalchemy import func

from app.schemas import OrderCreate, OrderUpdate
from app import crud
from app.config import SELLER_CONFIG
from app.database import reset_database, cache
from app.models import Order, Settlement
from app.db_connection import SessionLocal, engine, Base

# Create tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Management & Settlement System",
    description="Complete order processing with background settlement pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Home
# ---------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "🚀 Order Management & Settlement System",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "create_order": "POST /api/orders",
            "get_order": "GET /api/orders/{id}",
            "list_orders": "GET /api/orders",
            "update_order": "PUT /api/orders/{id}",
            "delete_order": "DELETE /api/orders/{id}",
            "settlements": "GET /api/settlements",
            "analytics": "GET /api/analytics"
        }
    }


# ---------------------------------------------------
# Health Check
# ---------------------------------------------------
@app.get("/health")
def health_check():
    db = SessionLocal()

    try:
        orders_count = db.query(func.count(Order.id)).scalar() or 0
        settlements_count = db.query(func.count(Settlement.id)).scalar() or 0

        return {
            "status": "healthy",
            "database": {
                "orders": int(orders_count),
                "settlements": int(settlements_count)
            },
            "cache": {
                "entries": len(cache)
            }
        }

    finally:
        db.close()


# ---------------------------------------------------
# Orders
# ---------------------------------------------------
@app.post("/api/orders", status_code=201)
def create_order(order: OrderCreate):

    print(f"\n{'='*80}")
    print("🆕 API: POST /api/orders")
    print(f"{'='*80}")

    try:
        return crud.create_order(
            product_id=order.product_id,
            customer_id=order.customer_id,
            seller_id=order.seller_id,
            amount=order.amount
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/{order_id}")
def get_order(order_id: int):

    print(f"\n🔍 API: GET /api/orders/{order_id}")

    try:
        return crud.get_order(order_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders")
def list_orders(skip: int = 0, limit: int = 10, status: Optional[str] = None):

    print("\n📋 API: GET /api/orders")

    try:
        return crud.list_orders(skip, limit, status)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/orders/{order_id}")
def update_order(order_id: int, order_update: OrderUpdate):

    print(f"\n✏️ API: PUT /api/orders/{order_id}")

    try:
        return crud.update_order(order_id, order_update.status)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/orders/{order_id}")
def delete_order(order_id: int):

    print(f"\n🗑️ API: DELETE /api/orders/{order_id}")

    try:
        return crud.delete_order(order_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# Settlements
# ---------------------------------------------------
@app.get("/api/settlements")
def list_settlements():

    print("\n💰 API: GET /api/settlements")

    try:
        return crud.get_settlements()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# Analytics
# ---------------------------------------------------
@app.get("/api/analytics")
def analytics():

    print("\n📊 API: GET /api/analytics")

    try:
        return crud.get_analytics()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# Seller Config
# ---------------------------------------------------
@app.get("/api/config/sellers")
def get_seller_config():

    print("\n⚙️ API: GET /api/config/sellers")

    return {
        "source": "MongoDB collection: seller_config",
        "sellers": SELLER_CONFIG
    }


# ---------------------------------------------------
# Reset System
# ---------------------------------------------------
@app.delete("/api/admin/reset")
def reset_system():

    print("\n🔄 API: DELETE /api/admin/reset")

    try:
        reset_database()
        return {"message": "System reset successfully"}

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=str(e))