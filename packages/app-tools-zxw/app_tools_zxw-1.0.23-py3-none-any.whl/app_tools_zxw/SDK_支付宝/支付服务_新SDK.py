"""
# File       : 支付服务_新SDK.py
# Time       ：2024/8/25 11:06
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import json
from uuid import uuid4
import hashlib
from alipay.aop.api.domain.AlipayTradePrecreateModel import AlipayTradePrecreateModel
from alipay.aop.api.request.AlipayTradePrecreateRequest import AlipayTradePrecreateRequest
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.util.SignatureUtils import verify_with_rsa
from alipay.aop.api.domain.AlipayTradeAppPayModel import AlipayTradeAppPayModel
from alipay.aop.api.request.AlipayTradeAppPayRequest import AlipayTradeAppPayRequest
from alipay.aop.api.request.AlipayTradeFastpayRefundQueryRequest import AlipayTradeFastpayRefundQueryModel, \
    AlipayTradeFastpayRefundQueryRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest, AlipayTradeQueryModel
from fastapi import FastAPI, HTTPException, status, Request
from starlette.datastructures import FormData
from app_tools_zxw.models_payment import PaymentMethod
from qrcode.main import QRCode
import qrcode
import enum


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class 支付服务:
    alipay_client: DefaultAlipayClient
    _rootUrl = "http://0.0.0.0"  # 根地址
    _支付状态回调地址 = "/callback/alipay"

    def __init__(self, app_id: str,
                 key应用私钥: str,
                 key支付宝公钥: str,
                 回调地址的根地址: str):
        """
        :param app_id:
        :param key应用私钥:
        :param key支付宝公钥:
        :param 回调地址的根地址:
        """
        self._rootUrl = 回调地址的根地址
        # 参数初始化
        alipay_config = AlipayClientConfig()
        alipay_config.server_url = 'https://openapi.alipay.com/gateway.do'
        alipay_config.app_id = app_id
        alipay_config.app_private_key = key应用私钥
        alipay_config.alipay_public_key = key支付宝公钥
        self.alipay_config = alipay_config

        self.alipay_client = DefaultAlipayClient(alipay_client_config=alipay_config)

    @staticmethod
    def 生成订单号() -> str:
        原始订单号 = str(uuid4())  # 或者其他生成逻辑
        return hashlib.md5(原始订单号.encode('utf-8')).hexdigest()

    def 发起二维码支付(self, 商户订单号: str, 价格: float, 商品名称: str) -> str:
        self.__订单信息校验(商户订单号, 价格, 商品名称)
        # 创建预下单请求
        model = AlipayTradePrecreateModel()
        model.out_trade_no = 商户订单号
        model.total_amount = str(价格)
        model.subject = 商品名称

        request = AlipayTradePrecreateRequest(biz_model=model)

        # 执行请求
        response = self.alipay_client.execute(request)
        res = json.loads(response)
        if res.get("code") == "10000":
            # 获取二维码链接
            qr_code_url = res.get("qr_code")
            return qr_code_url
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"支付宝支付接口调用失败: {res.get('msg')},{res.get('sub_msg')}")
            # raise Exception(f"支付宝支付接口调用失败: {res.get('msg')},{res.get('sub_msg')}")

    @staticmethod
    def 生成二维码(qr_code_url: str):
        qr = QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code_url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save("alipay_qr.png")
        print("二维码已生成，保存为 alipay_qr.png")

    def 发起APP支付(self,
                    商户订单号: str,
                    支付方式: PaymentMethod,
                    价格: float,
                    商品名称="") -> str:
        self.__订单信息校验(商户订单号, 价格, 商品名称)

        # App支付，将order_string返回给app即可
        model = AlipayTradeAppPayModel()
        model.out_trade_no = 商户订单号
        model.total_amount = str(价格)
        model.subject = 商品名称
        if 支付方式 == PaymentMethod.ALIPAY_APP:
            model.product_code = "QUICK_MSECURITY_PAY"
        elif 支付方式 == PaymentMethod.ALIPAY_H5:
            model.product_code = "QUICK_WAP_WAY"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="支付方式错误")

        request = AlipayTradeAppPayRequest(biz_model=model)
        request.notify_url = self._rootUrl + self._支付状态回调地址

        response = self.alipay_client.sdk_execute(request)

        # 如果是二维码支付，返回二维码链接（需要手动转换为二维码）
        if 支付方式 == PaymentMethod.ALIPAY_QR:
            return response
        # 如果是H5支付，返回支付链接
        elif 支付方式 == PaymentMethod.ALIPAY_H5:
            return response.body.get("body")
        # 如果是APP支付，返回支付信息
        else:
            return response.body

    def 查询订单(self, 商户订单号: str) -> OrderStatus:
        model = AlipayTradeQueryModel()
        model.out_trade_no = 商户订单号

        request = AlipayTradeQueryRequest(biz_model=model)
        response = self.alipay_client.execute(request)
        if response.get("code") == "10000" and response.get("msg") == "Success":
            if response.get("trade_status") == "TRADE_SUCCESS":
                return OrderStatus.PAID
            else:
                return OrderStatus.PENDING
        return OrderStatus.FAILED

    def 退款查询(self, 商户订单号: str) -> bool:
        model = AlipayTradeFastpayRefundQueryModel()
        model.out_trade_no = 商户订单号
        model.out_request_no = 商户订单号

        request = AlipayTradeFastpayRefundQueryRequest(biz_model=model)
        response = self.alipay_client.execute(request)
        return response.get("code") == "10000" and response.get("msg") == "Success"

    def 注册回调接口(self, app: FastAPI, async_func_支付成功):
        支付状态回调地址 = self._支付状态回调地址
        alipay_client = self.alipay_client

        @app.get(支付状态回调地址)
        async def 获取(request):
            print("支付回调get请求：", request)
            return "ok"

        @app.post(支付状态回调地址)
        async def 回调(postBody: Request):
            # 整理数据
            formData: FormData = await postBody.form()
            dataDict = {item[0]: item[1] for item in formData.items()}

            # 提取签名信息
            signature = dataDict.pop("sign", None)
            sign_type = dataDict.pop("sign_type", "RSA2")  # 默认使用RSA2

            # 校验数据
            try:
                # 使用支付宝公钥和签名类型进行验证
                success = verify_with_rsa(dataDict, signature, self.alipay_config.app_private_key)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"签名验证失败: {str(e)}")

            if success and dataDict.get("trade_status") in ("TRADE_SUCCESS", "TRADE_FINISHED"):
                data = {
                    "商户订单号": dataDict.get("out_trade_no"),
                    "支付宝交易号": dataDict.get("trade_no"),
                    "交易金额": dataDict.get("total_amount"),
                    "交易状态": dataDict.get("trade_status"),
                    "交易时间": dataDict.get("gmt_payment"),
                }
                return await async_func_支付成功(data)
            else:
                raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="支付失败")

    @staticmethod
    def __订单信息校验(商户订单号: str, 价格: float, 商品名称: str):
        if not 商户订单号 or len(商户订单号) >= 32:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商户订单号不能为空,或超过32位")
        if not 价格 or 价格 <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="价格不能为空,或小于0")
        if not 商品名称:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商品名称不能为空")
