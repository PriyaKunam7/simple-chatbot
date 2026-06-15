# app/models.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db_connection import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(String(100), nullable=False)
    customer_id = Column(String(100), nullable=False)
    seller_id = Column(String(100), nullable=False)

    amount = Column(Float, nullable=False)

    status = Column(String(50), default="pending", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    settlements = relationship(
        "Settlement",
        back_populates="order",
        cascade="all, delete"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "customer_id": self.customer_id,
            "seller_id": self.seller_id,
            "amount": float(self.amount),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    seller_id = Column(String(100), nullable=False)

    original_amount = Column(Float, nullable=False)

    commission = Column(Float, nullable=False)

    settlement_amount = Column(Float, nullable=False)

    status = Column(String(50), default="completed", nullable=False)

    settled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    order = relationship("Order", back_populates="settlements")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "seller_id": self.seller_id,
            "original_amount": float(self.original_amount),
            "commission": float(self.commission),
            "settlement_amount": float(self.settlement_amount),
            "status": self.status,
            "settled_at": self.settled_at.isoformat() if self.settled_at else None,
        }