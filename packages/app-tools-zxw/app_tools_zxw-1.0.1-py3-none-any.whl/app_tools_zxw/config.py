"""
# File       : config.py
# Time       ：2024/8/20 下午5:25
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import os
from datetime import timedelta

# postgresql数据库
DATABASE_URL = os.environ.get('DATABASE_URL')  # 读取docker配置的环境变量
if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://...:...@localhost/db-name"
    os.environ['DATABASE_URL'] = DATABASE_URL  # 设置环境变量, 以便在docker、alembic中读取

# redis数据库 redis://[[username]:[password]]@localhost:6379/0
redisUrl = "redis://[[username]:[password]]@localhost:6379/0"
redisUrl_测试and本机环境 = "redis://[[username]:[password]]@localhost:6379/0"


# jwt setting
class JWT:
    SECRET_KEY = "..."
    ALGORITHM = "HS256"
    expire_time = timedelta(days=7)


# 微信公众号
class WeChatPub:
    app_id = "..."
    app_secret = "..."
    scope = "snsapi_login"
    scope_qrcode_login = "snsapi_login"  # 二维码登录必须用snsapi_login
    state = "your_custom_state"  # 用于防止CSRF
    接口配置信息_Token = "..."  # 自己去微信公众号设置


# 微信小程序
class WeChatMini:
    app_id = "..."
    app_secret = "..."


# 阿里云
class Aliyun:
    ali_access_key_id = "..."
    ali_access_key_secret = "..."
    ali_secretNo_pool_key = "..."


# 支付专用
class WeChatPay:
    MCH_ID = '...'
    SECRET = '...'
    NONCE_STR = '...'
    KEY = '...'
    PAYMENT_NOTIFY_URL = 'https://.../wxpay_recall'
    REFUND_NOTIFY_URL = 'https://.../wxpay_recall'


# 发送邮件
class Email:
    sender = '...'  # 发件人
    server = 'smtp.163.com'  # 所使用的用来发送邮件的SMTP服务器
    username = '...'  # 发送邮箱的用户名和授权码（不是登录邮箱的密码）
    password = '...'  # 服务器: MVQDSPUQATBDOIFU / 自用电脑: FFHBMPJSXXFEEZIK


# AES密码密匙
class AESKey:
    key_web = "..."
    key_local = "..."
