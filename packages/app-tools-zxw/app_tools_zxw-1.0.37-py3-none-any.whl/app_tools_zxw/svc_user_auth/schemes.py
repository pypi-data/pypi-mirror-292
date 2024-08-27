"""
# File       : schemes.py
# Time       ：2024/8/26 下午8:53
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from typing import Union
from pydantic import BaseModel, Field


class Payload_Role(BaseModel):
    role_name: str
    app_name: str
    app_id: int


class Payload(BaseModel):
    sub: int = Field(..., title="用户id", description="用户id或其他唯一标识")
    username: Union[str, None] = None
    nickname: Union[str, None] = None
    roles: list[Payload_Role] = Field(..., title="角色", description="用户角色")


class 返回_login(BaseModel):
    access_token: str
    refresh_token: str
    user_info: Payload


class 请求_更新Token(BaseModel):
    refresh_token: str


class 返回_更新Token(BaseModel):
    access_token: str
    refresh_token: str


class 请求_检查Token_from_body(BaseModel):
    access_token: str


class 请求_验证角色_from_header(BaseModel):
    role_name: str
    app_name: str


class 返回_验证角色_from_header(BaseModel):
    status: bool


class 请求_分配或创建角色(BaseModel):
    user_id: int
    role_name: str
    app_name: str


class 返回_分配或创建角色(BaseModel):
    status: bool
    message: str


class 返回_获取_登录二维码URL(BaseModel):
    qr_code_url: str
