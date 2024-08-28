"""
# File       : schemes.py
# Time       ：2024/8/28 上午12:55
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pydantic import BaseModel
from app_tools_zxw.models_payment import PaymentMethod, OrderStatus


class 请求_微信url_创建支付(BaseModel):
    product_id: int
    user_id: str
    payment_method: PaymentMethod
    callback_url: str = None


class 返回_微信url_创建支付(BaseModel):
    order_number: str
    payment_url: str  # 可以是二维码链接或直接支付链接


class 返回_微信url_订单状态(BaseModel):
    order_number: str
    status: OrderStatus


class 请求_支付宝url_创建订单(BaseModel):
    amount: float  # 创建支付时，该处值无效，订单金额根据创建时订单金额而定
    user_id: str
    product_id: int
    callback_url: str
    app_id: str


class 返回_支付宝url_订单信息(BaseModel):
    order_number: str
    user_id: str
    total_amount: float
    product_id: int
    app_id: str
    status: str


class 请求_支付宝url_发起支付(BaseModel):
    order_number: str  # 创建订单时不用传入
    user_id: str
    product_id: int
    callback_url: str
    app_id: str


class 返回_支付宝url_支付信息(BaseModel):
    transaction_id: str
    payment_status: str
    amount: float
    order_id: int
    app_id: str
    qr_uri: str
