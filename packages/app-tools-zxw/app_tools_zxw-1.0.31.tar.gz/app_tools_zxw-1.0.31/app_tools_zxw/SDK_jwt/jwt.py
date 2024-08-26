"""
# File       : jwt.py
# Time       ：2024/8/20 下午5:27
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
    1. create_jwt_token() 生成JWT令牌
    2. get_current_user() 从当前请求中，读取令牌，并验证用户身份。
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
# 用户自定义部分
from config import JWT
from db.get_db import get_db
from db.models import User

ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60 * 7  # 默认令牌过期时间，单位是分钟
# tokenUrl是登录页面的URL, 用于文档测试
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/account/login-form/")


def create_jwt_token(data: dict, expires_delta: timedelta = None):
    """
    生成JWT令牌
    :param data:
    :param expires_delta: 过期时间。如果不设置，将使用默认的过期时间：ACCESS_TOKEN_EXPIRE_MINUTES
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT.SECRET_KEY, algorithm=JWT.ALGORITHM)
    return encoded_jwt


def check_jwt_token(token: str):
    """
    验证JWT令牌
    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, JWT.SECRET_KEY, algorithms=[JWT.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_db)) -> User:
    """
    从当前请求中，读取令牌，并验证用户身份。

    使用方法：在需要验证用户身份的路由上加上Depends(get_current_user)
            如： async def role_checker(user: User = Depends(get_current_user)):
                    ...

    前端请求格式：
        请求头的格式应该是Authorization，前端发送请求时，应该在请求头中添加：Authorization: Bearer token。

        uniApp中的添加方式如下：
    ```
        uni.request({
            url: 'https://...'
            method: 'POST',
            header: {
                'Authorization': 'Bearer ' + token
            },
            data: {
                ...
            },
            success: (res) => {
                ...
            }
        })
    ```
    :param token:
    :param db:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"Authenticate": "Bearer "},
    )
    try:
        payload = jwt.decode(token, JWT.SECRET_KEY, algorithms=[JWT.ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_exp = payload.get("exp")
        if datetime.utcfromtimestamp(token_exp) < datetime.utcnow():
            raise credentials_exception

        result = await db.execute(select(User).filter(User.id == user_id))
        user: User = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user
