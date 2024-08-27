"""
# File       : apis.py
# Time       ：2024/8/26 下午10:19
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
import httpx
from app_tools_zxw.svc_user_auth.schemes import *

# get router from os environment
router = APIRouter(prefix="/user_center", tags=["用户管理"])

svc_user = "http://127.0.0.1:8101"

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
@router.post("/wechat/get-login-qrcode", response_model=返回_获取_登录二维码URL)
async def 获取_登录二维码URL(request: WeChatQRCodeRequest):
    # 调用用户管理微服务获取微信二维码URL
    # 请求URL DEMO ： http://127.0.0.1:8101/wechat/qr-login/get-qrcode
    print({"WECHAT_REDIRECT_URI": request.WECHAT_REDIRECT_URI})
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/wechat/qr-login/get-qrcode",
            json={"WECHAT_REDIRECT_URI": request.WECHAT_REDIRECT_URI}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to get QR code")
        return response.json()


@router.post("/wechat/login", response_model=返回_login)
async def 微信登录(request: WeChatLoginRequest):
    # 调用用户管理微服务进行微信登录
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/wechat/qr-login/login/",
            params={"code": request.code, "app_name": request.app_name}
        )
        if response.status_code != 200:
            print(response.content)
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to login with WeChat" if response.content else response.content)
        return response.json()


@router.post("/token/refresh", response_model=返回_更新Token)
async def 更新Token(request: TokenRefreshRequest):
    # 调用用户管理微服务刷新Token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/token/refresh-token/",
            json={"refresh_token": request.refresh_token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to refresh token")
        return response.json()


@router.post("/get-current-user", response_model=Payload)
async def 获取当前用户(request: Request) -> Payload:
    # 将请求头中的Token传递给用户管理微服务
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Token not found")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/token/get-current-user/",
            headers={"Authorization": token}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to get current user")

    return response.json()


@router.get("/roles/role-auth", response_model=返回_验证角色_from_header)
async def 验证角色_from_header(role_name: str, app_name: str, token: str = Depends(oauth2_scheme)):
    # 调用用户管理微服务进行角色验证
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{svc_user}/api/roles/role_auth/",
            json=请求_验证角色_from_header(role_name=role_name, app_name=app_name).model_dump(),
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Role not authorized")
        return response.json()
