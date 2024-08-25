"""
# File       : models.py
# Time       ：2024/8/25 06:57
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import enum


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(enum.Enum):
    WECHAT_H5 = "wechat_h5"
    WECHAT_QR = "wechat_qr"
    WECHAT_MINI = "wechat_mini"
    WECHAT_APP = "wechat_app"
    ALIPAY_H5 = "alipay_h5"
    ALIPAY_QR = "alipay_qr"
    ALIPAY_APP = "alipay_app"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
