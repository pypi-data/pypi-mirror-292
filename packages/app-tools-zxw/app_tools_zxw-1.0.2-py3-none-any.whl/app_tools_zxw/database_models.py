"""
# File       : models.py
# Time       ：2024/8/25 06:57
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(enum.Enum):
    WECHAT_H5 = "wechat_h5"
    WECHAT_MINI = "wechat_mini"
    WECHAT_APP = "wechat_app"
    ALIPAY_H5 = "alipay_h5"
    ALIPAY_APP = "alipay_app"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class Product(Base):
    """产品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    app_id = Column(String, index=True)  # The ID of the app the product belongs to
    price = Column(Float, nullable=False)

    orders = relationship("Order", back_populates="product")


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    # app_id = Column(String, index=True)
    user_id = Column(String, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # 自动更新时间
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="orders")
    payments = relationship("Payment", back_populates="order")


class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_id = Column(String, unique=True)
    payment_status = Column(String)
    callback_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # 自动更新时间

    order = relationship("Order", back_populates="payments")
