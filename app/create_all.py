files = {
    'app/__init__.py': '''"""Order Management System"""
__version__ = "1.0.0"
''',
    
    'app/config.py': '''SELLER_CONFIG = {
    "SELLER001": {"name": "Tech Store", "commission_rate": 0.05, "active": True},
    "SELLER002": {"name": "Fashion Store", "commission_rate": 0.10, "active": True},
    "SELLER003": {"name": "Book Store", "commission_rate": 0.03, "active": True}
}

def validate_seller(seller_id: str) -> bool:
    seller = SELLER_CONFIG.get(seller_id)
    return seller and seller.get("active", False)

def get_commission_rate(seller_id: str) -> float:
    seller = SELLER_CONFIG.get(seller_id)
    return seller.get("commission_rate", 0.05) if seller else 0.05
''',

    'app/models.py': '''from datetime import datetime

class Order:
    def __init__(self, id, product_id, customer_id, seller_id, amount, status="pending", created_at=None):
        self.id = id
        self.product_id = product_id
        self.customer_id = customer_id
        self.seller_id = seller_id
        self.amount = amount
        self.status = status
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "customer_id": self.customer_id,
            "seller_id": self.seller_id,
            "amount": self.amount,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

class Settlement:
    def __init__(self, id, order_id, seller_id, original_amount, commission, settlement_amount, status="completed", settled_at=None):
        self.id = id
        self.order_id = order_id
        self.seller_id = seller_id
        self.original_amount = original_amount
        self.commission = commission
        self.settlement_amount = settlement_amount
        self.status = status
        self.settled_at = settled_at or datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "seller_id": self.seller_id,
            "original_amount": self.original_amount,
            "commission": self.commission,
            "settlement_amount": self.settlement_amount,
            "status": self.status,
            "settled_at": self.settled_at.isoformat()
        }
''',

    'app/database.py': '''from typing import Dict, List, Optional
from app.models import Order, Settlement

orders_db: Dict[int, Order] = {}
settlements_db: Dict[int, Settlement] = {}
cache: Dict[str, dict] = {}

order_counter = 0
settlement_counter = 0

def create_order(product_id: str, customer_id: str, seller_id: str, amount: float) -> Order:
    global order_counter
    order_counter += 1
    order = Order(order_counter, product_id, customer_id, seller_id, amount, "pending")
    orders_db[order_counter] = order
    print(f"💾 DATABASE: Order #{order_counter} saved to PostgreSQL")
    return order

def get_order(order_id: int) -> Optional[Order]:
    return orders_db.get(order_id)

def get_all_orders(skip: int = 0, limit: int = 10) -> List[Order]:
    all_orders = list(orders_db.values())
    return all_orders[skip:skip + limit]

def update_order_status(order_id: int, new_status: str) -> Optional[Order]:
    order = orders_db.get(order_id)
    if order:
        old_status = order.status
        order.status = new_status
        print(f"📝 DATABASE: Order #{order_id} status: {old_status} → {new_status}")
        return order
    return None

def delete_order(order_id: int) -> bool:
    order = orders_db.get(order_id)
    if order:
        order.status = "cancelled"
        print(f"🗑️ DATABASE: Order #{order_id} cancelled")
        return True
    return False

def create_settlement(order_id: int, seller_id: str, original_amount: float, 
                     commission: float, settlement_amount: float) -> Settlement:
    global settlement_counter
    settlement_counter += 1
    settlement = Settlement(settlement_counter, order_id, seller_id, 
                          original_amount, commission, settlement_amount, "completed")
    settlements_db[settlement_counter] = settlement
    print(f"💰 DATABASE: Settlement #{settlement_counter} saved to PostgreSQL")
    return settlement

def get_all_settlements() -> List[Settlement]:
    return list(settlements_db.values())

def cache_order(order_id: int, order_data: dict):
    cache[f"order:{order_id}"] = order_data
    print(f"⚡ REDIS: Order #{order_id} cached")

def get_cached_order(order_id: int) -> Optional[dict]:
    cache_key = f"order:{order_id}"
    if cache_key in cache:
        print(f"⚡ REDIS: Cache HIT for Order #{order_id}")
        return cache[cache_key]
    print(f"⚡ REDIS: Cache MISS for Order #{order_id}")
    return None

def clear_cache(order_id: int):
    cache_key = f"order:{order_id}"
    if cache_key in cache:
        del cache[cache_key]
        print(f"⚡ REDIS: Cache cleared for Order #{order_id}")

def get_analytics() -> dict:
    print("📊 PYSPARK: Processing analytics...")
    
    total_orders = len(orders_db)
    total_revenue = sum(o.amount for o in orders_db.values())
    total_settled = sum(s.settlement_amount for s in settlements_db.values())
    total_commission = sum(s.commission for s in settlements_db.values())
    
    status_breakdown = {}
    for order in orders_db.values():
        status = order.status
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    seller_revenue = {}
    for order in orders_db.values():
        seller = order.seller_id
        seller_revenue[seller] = seller_revenue.get(seller, 0) + order.amount
    
    return {
        "overview": {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "total_settled": round(total_settled, 2),
            "total_commission": round(total_commission, 2)
        },
        "status_breakdown": status_breakdown,
        "seller_revenue": seller_revenue,
        "cache_size": len(cache)
    }

def reset_database():
    global order_counter, settlement_counter
    orders_db.clear()
    settlements_db.clear()
    cache.clear()
    order_counter = 0
    settlement_counter = 0
    print("🔄 DATABASE: All databases reset")
''',

    'app/events.py': '''import json

def publish_event(event_type: str, event_data: dict):
    print(f"📢 KAFKA: Event published to topic '{event_type}'")
    print(f"   Data: {json.dumps(event_data, indent=2)}")
    return True

def publish_order_created(order_id: int, seller_id: str, amount: float):
    event_data = {"order_id": order_id, "seller_id": seller_id, "amount": amount}
    publish_event("order.created", event_data)
    return event_data

def publish_order_updated(order_id: int, old_status: str, new_status: str):
    event_data = {"order_id": order_id, "old_status": old_status, "new_status": new_status}
    publish_event("order.updated", event_data)
    return event_data

def publish_settlement_completed(settlement_id: int, order_id: int, amount: float):
    event_data = {"settlement_id": settlement_id, "order_id": order_id, "amount": amount}
    publish_event("settlement.completed", event_data)
    return event_data
''',

    'app/settlement.py': '''import time
from app.config import get_commission_rate
from app.database import create_settlement, update_order_status
from app.events import publish_settlement_completed

def process_settlement(order_id: int, seller_id: str, amount: float):
    print(f"\\n{'='*60}")
    print(f"⚙️ CELERY WORKER: Processing settlement for Order #{order_id}")
    print(f"{'='*60}")
    
    try:
        commission_rate = get_commission_rate(seller_id)
        print(f"📋 MONGODB: Commission rate for {seller_id}: {commission_rate*100}%")
        
        commission = amount * commission_rate
        settlement_amount = amount - commission
        
        print(f"💵 CALCULATION:")
        print(f"   Original Amount: ${amount:.2f}")
        print(f"   Commission ({commission_rate*100}%): ${commission:.2f}")
        print(f"   Settlement Amount: ${settlement_amount:.2f}")
        
        print(f"⏳ PROCESSING: Simulating bank API call (2 seconds)...")
        time.sleep(2)
        
        settlement = create_settlement(order_id, seller_id, amount, commission, settlement_amount)
        update_order_status(order_id, "settled")
        publish_settlement_completed(settlement.id, order_id, settlement_amount)
        
        print(f"✅ CELERY WORKER: Settlement completed successfully!")
        print(f"{'='*60}\\n")
        
        return settlement
        
    except Exception as e:
        print(f"❌ CELERY WORKER: Settlement failed - {str(e)}")
        print(f"{'='*60}\\n")
        raise
''',

    'app/crud.py': '''from typing import Optional
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
    if not validate_seller(seller_id):
        raise HTTPException(status_code=400, detail=f"Invalid seller_id: {seller_id}")
    
    order = db_create_order(product_id, customer_id, seller_id, amount)
    cache_order(order.id, order.to_dict())
    publish_order_created(order.id, seller_id, amount)
    process_settlement(order.id, seller_id, amount)
    
    return {
        "order_id": order.id,
        "status": "created",
        "message": "Order created and settlement processing completed"
    }

def get_order(order_id: int) -> dict:
    cached_order = get_cached_order(order_id)
    if cached_order:
        return cached_order
    
    order = db_get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found")
    
    order_dict = order.to_dict()
    cache_order(order_id, order_dict)
    return order_dict

def list_orders(skip: int = 0, limit: int = 10, status: Optional[str] = None) -> dict:
    orders = db_get_all_orders(skip, limit)
    
    if status:
        orders = [o for o in orders if o.status == status]
    
    return {
        "total": len(orders),
        "count": len(orders),
        "orders": [o.to_dict() for o in orders]
    }

def update_order(order_id: int, new_status: str) -> dict:
    order = db_get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found")
    
    old_status = order.status
    db_update_order_status(order_id, new_status)
    clear_cache(order_id)
    publish_order_updated(order_id, old_status, new_status)
    
    return {"message": f"Order #{order_id} updated from '{old_status}' to '{new_status}'"}

def delete_order(order_id: int) -> dict:
    order = db_get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found")
    
    success = db_delete_order(order_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel order")
    
    clear_cache(order_id)
    return {"message": f"Order #{order_id} cancelled successfully"}

def get_settlements() -> dict:
    settlements = get_all_settlements()
    return {
        "total": len(settlements),
        "settlements": [s.to_dict() for s in settlements]
    }

def get_analytics() -> dict:
    return db_get_analytics()
''',

    'app/main.py': '''from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.schemas import OrderCreate, OrderUpdate
from app import crud
from app.config import SELLER_CONFIG
from app.database import reset_database

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

@app.get("/health")
def health_check():
    from app.database import orders_db, settlements_db, cache
    return {
        "status": "healthy",
        "database": {"orders": len(orders_db), "settlements": len(settlements_db)},
        "cache": {"entries": len(cache)}
    }

@app.post("/api/orders", status_code=201)
def create_order(order: OrderCreate):
    print(f"\\n{'='*80}")
    print(f"🆕 API: POST /api/orders")
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
    print(f"\\n🔍 API: GET /api/orders/{order_id}")
    try:
        return crud.get_order(order_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders")
def list_orders(skip: int = 0, limit: int = 10, status: Optional[str] = None):
    print(f"\\n📋 API: GET /api/orders")
    try:
        return crud.list_orders(skip, limit, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/orders/{order_id}")
def update_order(order_id: int, order_update: OrderUpdate):
    print(f"\\n✏️ API: PUT /api/orders/{order_id}")
    try:
        return crud.update_order(order_id, order_update.status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/orders/{order_id}")
def delete_order(order_id: int):
    print(f"\\n🗑️ API: DELETE /api/orders/{order_id}")
    try:
        return crud.delete_order(order_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settlements")
def list_settlements():
    print(f"\\n💰 API: GET /api/settlements")
    try:
        return crud.get_settlements()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
def analytics():
    print(f"\\n📊 API: GET /api/analytics")
    try:
        return crud.get_analytics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/sellers")
def get_seller_config():
    print(f"\\n⚙️ API: GET /api/config/sellers")
    return {"source": "MongoDB collection: seller_config", "sellers": SELLER_CONFIG}

@app.delete("/api/admin/reset")
def reset_system():
    print(f"\\n🔄 API: DELETE /api/admin/reset")
    try:
        reset_database()
        return {"message": "System reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
}

for filepath, content in files.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filepath}")

print("\n🎉 All files created! Run: uvicorn app.main:app --reload")