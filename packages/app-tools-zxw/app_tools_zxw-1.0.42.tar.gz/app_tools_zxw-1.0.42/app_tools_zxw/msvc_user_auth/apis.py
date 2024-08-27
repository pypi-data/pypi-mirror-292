"""
# File       : apis.py
# Time       ：2024/8/26 下午10:19
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx
from app_tools_zxw.msvc_user_auth.schemes import *

# get router from os environment
router = APIRouter(prefix="/user_center", tags=["用户管理"])

svc_user = "http://127.0.0.1:8101"

# OAuth2PasswordBearer 实例
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user_center/account/login-form/")


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


@router.post("/account/register", response_model=返回_login)
async def 账号密码_注册(data: 请求_账号密码_注册):
    # 调用用户管理微服务进行普通注册
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/account/register/",
            json=data.model_dump()
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else "Failed to register")
        return response.json()


@router.post("/account/login", response_model=返回_login)
async def 账号密码_登录(data: 请求_账号密码_登录):
    # 调用用户管理微服务进行普通登录
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/account/login/",
            json=data.model_dump()
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else "Failed to login")
        return response.json()


@router.post("/account/login-form", response_model=返回_login)
async def 账号密码_登录_Form数据(login_info: OAuth2PasswordRequestForm = Depends()):
    data = 请求_账号密码_登录(username=login_info.username, password=login_info.password)
    return await 账号密码_登录(data)


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
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else "Failed to login with WeChat")
        return response.json()


@router.post("/token/refresh", response_model=返回_更新Token)
async def 更新Token(request: TokenRefreshRequest, token: str = Depends(oauth2_scheme)):
    # 调用用户管理微服务刷新Token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/token/refresh-token/",
            json={"refresh_token": request.refresh_token},
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else "Failed to refresh token")
        return response.json()


@router.post("/get-current-user", response_model=Payload)
async def 获取当前用户(token: str = Depends(oauth2_scheme)) -> Payload:
    # 将请求头中的Token传递给用户管理微服务
    if not token:
        raise HTTPException(status_code=401, detail="interface Token not found")

    # header
    header = {"Authorization": f"Bearer {token}"}
    print(header)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{svc_user}/api/token/get-current-user/",
            headers=header
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json() if response.content else "Failed to get current user")

    return response.json()


@router.post("/roles/role-auth", response_model=返回_验证角色_from_header)
async def 验证角色_from_header(info: 请求_验证角色_from_header, token: str = Depends(oauth2_scheme)):
    # 调用用户管理微服务进行角色验证
    async with httpx.AsyncClient() as client:
        # url demo: http://localhost:8101/api/roles/role-auth/
        response = await client.post(
            f"{svc_user}/api/roles/role-auth/",
            json=请求_验证角色_from_header(role_name=info.role_name, app_name=info.app_name).model_dump_json(),
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else "Failed to auth role")

        return response.json()


if __name__ == '__main__':
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="app-tools-zxw 接口-用户微服务")
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
