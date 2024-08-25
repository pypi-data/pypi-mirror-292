"""
# File       : 微信支付.py
# Time       ：2024/8/25 07:11
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from uuid import uuid4
import hashlib
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app_tools_zxw.database_models import PaymentMethod, OrderStatus, Payment, Order
from app_tools_zxw.config import WeChatPay, WeChatPub


class 支付服务_二维码:
    @staticmethod
    async def 生成支付链接(支付方式: PaymentMethod,
                           交易号: str,
                           金额: float,
                           回调地址: str,
                           用户ip地址: str,
                           商品描述: str = "二维码支付") -> str:
        if 支付方式 in [PaymentMethod.WECHAT_H5, PaymentMethod.WECHAT_MINI, PaymentMethod.WECHAT_APP]:
            url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
            请求数据 = {
                "appid": WeChatPub.app_id,
                "mch_id": WeChatPay.MCH_ID,
                "nonce_str": 支付服务_二维码.__生成订单号(),
                "body": 商品描述,
                "out_trade_no": 交易号,
                "total_fee": int(金额 * 100),  # 单位为分
                "spbill_create_ip": 用户ip地址,
                "notify_url": 回调地址,
                "trade_type": "NATIVE",  # 使用NATIVE表示二维码支付
            }

            # 签名计算
            签名字符串 = "&".join([f"{k}={v}" for k, v in sorted(请求数据.items())]) + "&key=YOUR_API_KEY"
            请求数据["sign"] = hashlib.md5(签名字符串.encode('utf-8')).hexdigest().upper()

            # 发起异步请求
            async with httpx.AsyncClient() as 客户端:
                响应 = await 客户端.post(url, data=请求数据)

            # 解析返回值
            if 响应.status_code == 200:
                响应数据 = 响应.json()
                if 响应数据.get("return_code") == "SUCCESS" and 响应数据.get("result_code") == "SUCCESS":
                    return 响应数据["code_url"]  # 微信支付二维码链接
                else:
                    raise HTTPException(status_code=400, detail="微信支付错误")
            else:
                raise HTTPException(status_code=500, detail="微信API错误")

        else:
            raise HTTPException(status_code=400, detail="不支持的支付方式")

    @staticmethod
    def __生成订单号() -> str:
        return str(uuid4())

    @staticmethod
    async def demo_创建订单和支付记录(db: AsyncSession,
                                      商品,
                                      用户ID: str,
                                      支付方式: PaymentMethod,
                                      回调地址: str,
                                      用户ip地址: str):
        订单号 = 支付服务_二维码.__生成订单号()

        # 创建订单
        订单 = Order(
            order_number=订单号,
            user_id=用户ID,
            total_amount=商品.price,
            status=OrderStatus.PENDING,
            product_id=商品.id
        )
        db.add(订单)
        await db.commit()
        await db.refresh(订单)

        # 创建支付记录
        交易号 = str(uuid4())
        支付记录 = Payment(
            order_id=订单.id,
            payment_method=支付方式,
            amount=商品.price,
            transaction_id=交易号,
            payment_status=OrderStatus.PENDING.value,
            callback_url=回调地址
        )
        db.add(支付记录)
        await db.commit()
        await db.refresh(支付记录)

        # 生成支付链接或二维码 (异步调用)
        支付链接 = await 支付服务_二维码.生成支付链接(支付方式, 交易号, 商品.price, 回调地址, 用户ip地址, 商品.name)

        return 订单号, 支付链接
