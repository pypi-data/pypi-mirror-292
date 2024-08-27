"""
# File       : 支付服务_新SDK.py
# Time       ：2024/8/25 11:06
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pathlib import Path
from typing import Union
import json
from uuid import uuid4
import hashlib

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

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
from fastapi import FastAPI, HTTPException, status, Request, APIRouter
from starlette.datastructures import FormData
from app_tools_zxw.models_payment import PaymentMethod, OrderStatus
from qrcode.main import QRCode
import qrcode
from pydantic import BaseModel, Field


class PaymentResult(BaseModel):
    商户订单号: str = Field(..., title="商户订单号", description="transaction_id")
    支付平台交易号: str = Field(..., title="支付平台交易号", description="")
    交易金额: float = Field(..., title="交易金额", description="amount")
    交易状态: OrderStatus
    支付时间: str = Field(..., title="支付时间", description="payment_time")
    支付账号: str = None
    支付方式: PaymentMethod
    支付失败原因: str = None
    备注: str = None


def crt证书_解析成_pem公钥(cert_file_path: Path):
    # 读取证书文件
    with open(cert_file_path, "rb") as cert_file:
        cert_data = cert_file.read()

    # 加载证书
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

    # 提取公钥
    public_key = cert.public_key()

    # 将公钥转换为PEM格式字符串
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8').strip()

    return public_key_pem


class 支付服务:
    alipay_client: DefaultAlipayClient
    _回调路径的根地址 = "http://0.0.0.0"  # 如果需要回调处理的话，此处必填
    _回调路径 = "/callback/"

    def __init__(self, app_id: str,
                 key应用私钥: str,
                 key支付宝公钥: Union[str, Path],
                 回调路径的根地址: str,
                 ):
        """
        :param app_id:
        :param key应用私钥:
        :param key支付宝公钥: 如果是字符串，直接传入公钥字符串；如果是Path，读取转换后传入，传入公钥文件路径
        :param 回调路径的根地址: 如果需要回调处理的话，此处必填
        """
        self._支付服务器根地址 = 回调路径的根地址
        #
        if isinstance(key支付宝公钥, Path):
            if key支付宝公钥.suffix == ".crt":
                key支付宝公钥 = crt证书_解析成_pem公钥(key支付宝公钥)
                print("app-tools-zxw/SDK_支付宝/支付服务_新SDK.py: key支付宝公钥=", key支付宝公钥)
            else:
                raise ValueError("支付宝公钥文件必须是.crt文件")
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

        print("app-tools-zxw/SDK_支付宝/支付服务_新SDK.py: 发起二维码支付: request=", request.get_params())
        print("app-tools-zxw/SDK_支付宝/支付服务_新SDK.py: 发起二维码支付: model=", model.to_alipay_dict())

        # 执行请求
        try:
            response = self.alipay_client.execute(request)
            print("app-tools-zxw/SDK_支付宝/支付服务_新SDK.py: 发起二维码支付: response=", response)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"支付宝支付接口调用失败: {str(e)}")
        res = json.loads(response)
        if res.get("code") == "10000":
            # 获取二维码链接
            qr_code_url = res.get("qr_code")
            return qr_code_url
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"支付宝支付接口调用失败: {res.get('msg')},{res.get('sub_msg')}")
            # raise Exception(f"支付宝支付接口调用失败: {res.get('msg')},{res.get('sub_msg')}")

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
        request.notify_url = self._回调路径的根地址 + self._回调路径

        print("app-tools-zxw/SDK_支付宝/支付服务_新SDK.py: 发起APP支付: request=", request.get_params())
        print("app-tools-zxw/SDK_支付宝/支付服务_新SDK.py: 发起APP支付: model=", model.to_alipay_dict())

        response = self.alipay_client.sdk_execute(request)
        try:
            response = json.loads(response)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"发起APP支付,结果解析失败: {str(e)}")

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
        try:
            response = json.loads(response)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"查询订单,结果解析失败: {str(e)}")
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
        try:
            response = json.loads(response)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"退款查询,结果解析失败: {str(e)}")
        return response.get("code") == "10000" and response.get("msg") == "Success"

    def 注册回调接口(self, app: Union[FastAPI, APIRouter], async_func_支付成功):
        支付状态回调地址 = self._回调路径
        alipay_client = self.alipay_client

        @app.get(支付状态回调地址)
        async def 回调_验证地址(request):
            print("支付回调get请求：", request)
            return "ok"

        @app.post(支付状态回调地址)
        async def 回调_支付完成处理(postBody: Request):
            # 整理数据
            formData: FormData = await postBody.form()
            dataDict = {item[0]: item[1] for item in formData.items()}
            print("支付回调post请求,dataDict=", dataDict)

            # 提取签名信息
            signature = dataDict.pop("sign", None)
            sign_type = dataDict.pop("sign_type", "RSA2")  # 默认使用RSA2

            # 校验数据
            try:
                # 使用支付宝公钥和签名类型进行验证
                success = verify_with_rsa(dataDict, signature, self.alipay_config.app_private_key)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"签名验证失败: {str(e)}")

            # 校验成功，处理支付结果
            if not success:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="签名验证失败")

            result = PaymentResult(
                商户订单号=dataDict.get("out_trade_no"),
                支付平台交易号=dataDict.get("trade_no"),
                交易金额=float(dataDict.get("total_amount")),
                交易状态=OrderStatus.PENDING,
                支付时间=dataDict.get("gmt_payment"),
                支付方式=PaymentMethod.ALIPAY_H5,
                支付账号=dataDict.get("buyer_logon_id"),
                备注=dataDict.get("body")
            )
            if dataDict.get("trade_status") == "TRADE_SUCCESS":
                result.交易状态 = OrderStatus.PAID
            elif dataDict.get("trade_status") == "TRADE_CLOSED":
                result.交易状态 = OrderStatus.FAILED
                result.支付失败原因 = dataDict.get("TRADE_CLOSED")
            elif dataDict.get("trade_status") == "TRADE_FINISHED":
                # 交易完成，不可退款.TRADE_FINISHED与TRADE_SUCCESS的区别是TRADE_FINISHED是不可退款的.
                result.交易状态 = OrderStatus.FINISHED
            else:
                result.支付失败原因 = dataDict.get("trade_status")
                result.交易状态 = OrderStatus.FAILED

            return await async_func_支付成功(result)

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

    @staticmethod
    def __订单信息校验(商户订单号: str, 价格: float, 商品名称: str):
        if not 商户订单号 or len(商户订单号) > 32:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商户订单号不能为空,或超过32位")
        if not 价格 or 价格 <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="价格不能为空,或小于0")
        if not 商品名称:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商品名称不能为空")
