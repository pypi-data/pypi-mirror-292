"""
# File       : apis.py
# Time       ：2024/8/26 下午10:19
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
import httpx

router = APIRouter(prefix="user_center", tags=["用户管理"])
svc_user = "http://localhost:8101"

# OAuth2PasswordBearer 实例
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/check-token-from-body/")


# Pydantic 模型
class WeChatQRCodeRequest(BaseModel):
    WECHAT_REDIRECT_URI: str


class WeChatLoginRequest(BaseModel):
    code: str
    app_name: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class RoleAuthRequest(BaseModel):
    role_name: str
    app_name: str


# 核心服务部分
@router.post("/core/wechat/get-login-qrcode", response_model=dict)
async def core_get_login_qrcode(request: WeChatQRCodeRequest):
    # 调用用户管理微服务获取微信二维码URL
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/wechat/login/get-login-qrcode",
            params={"WECHAT_REDIRECT_URI": request.WECHAT_REDIRECT_URI}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to get QR code")
        return response.json()


@router.post("/core/wechat/login", response_model=dict)
async def core_wechat_login(request: WeChatLoginRequest):
    # 调用用户管理微服务进行微信登录
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/wechat/login/wechat-login/",
            params={"code": request.code, "app_name": request.app_name}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to login with WeChat")
        return response.json()


@router.post("/core/token/refresh", response_model=dict)
async def core_refresh_token(request: TokenRefreshRequest):
    # 调用用户管理微服务刷新Token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/token/refresh-token/",
            params={"refresh_token": request.refresh_token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to refresh token")
        return response.json()


@router.get("/core/roles/role-auth", response_model=dict)
async def core_role_auth(role_name: str, app_name: str, token: str = Depends(oauth2_scheme)):
    # 调用用户管理微服务进行角色验证
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{svc_user}/api/roles/role_auth/",
            params={"role_name": role_name, "app_name": app_name},
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Role not authorized")
        return response.json()
