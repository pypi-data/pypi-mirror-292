"""
# File       : 支付服务.py
# Time       ：2024/8/25 10:59
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from alipay import AliPay, DCAliPay, ISVAliPay
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status, Request
from typing import List
from starlette.datastructures import FormData
from app_tools_zxw.SDK_支付宝.models import callback支付结果pydantic, 退款查询返回结果pydantic, 订单查询pydantic


class Alipay二次开发:
    alipay: AliPay
    _rootUrl = "http://0.0.0.0"  # 根地址
    _支付状态回调地址 = "/callback/alipay"

    def init(self, 回调根地址, appid, key应用私钥, key支付宝公钥):
        self._rootUrl = 回调根地址
        # 参数初始化
        self.alipay = AliPay(
            appid=appid,
            app_private_key_string=key应用私钥,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=key支付宝公钥,
            app_notify_url=None,  # 默认回调url
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False  # 默认False
        )

    def 下单(self, orderID="订单号", price=0.01, 商品名称=""):
        # App支付，将order_string返回给app即可
        order_string = self.alipay.api_alipay_trade_app_pay(
            out_trade_no=orderID,
            total_amount=price,
            subject=商品名称,
            notify_url=self._rootUrl + self._支付状态回调地址
        )
        return order_string

    def 订阅(self):
        self.alipay.api_alipay_trade_app_pay()

    def 退款查询(self, orderID="商户订单号") -> bool:
        res = self.alipay.api_alipay_trade_fastpay_refund_query(orderID, out_trade_no=orderID)
        result = 退款查询返回结果pydantic(**res)
        if result.code == "10000":
            if result.msg == "Success":
                return True
        return False

    def 历史订单查询(self, 商户订单号):
        res = self.alipay.api_alipay_trade_query(out_trade_no=商户订单号)
        result = 订单查询pydantic(**res)
        # 订单存在
        if result.msg == "Success":
            # 付款成功
            if result.trade_status == "TRADE_SUCCESS":
                return True
            # 付款失败
            else:
                return result.trade_status
        # 订单不存在
        return result.sub_msg

    def 注册回调接口(self, app: FastAPI, 支付成功func):
        支付状态回调地址 = self._支付状态回调地址
        alipay = self.alipay

        @app.get(支付状态回调地址)
        async def 获取(request):
            print("支付回调get请求：", request)
            return "ok"

        @app.post(支付状态回调地址)
        async def 回调(postBody: Request):
            # 整理数据
            formData: FormData = await postBody.form()
            dataItemsList = formData.items()
            dataDict = {item[0]: item[1] for item in dataItemsList}
            # 校验数据
            dataPydantic = callback支付结果pydantic(**dataDict)
            data = dataPydantic.dict()
            #
            signature = data.pop("sign")
            # verify
            success = alipay.verify(data, signature)
            if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
                return await 支付成功func(dataPydantic)
            else:
                raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="支付失败")

#
# 定义 pydantic 数据结构
#
