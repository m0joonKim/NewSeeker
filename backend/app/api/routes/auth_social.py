from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.core.config import settings
from app.models import Token, User, ProviderEnum
from app.core.security import create_access_token
from app.api.deps import get_db, get_current_user
import httpx
from datetime import timedelta
from authlib.integrations.starlette_client import OAuth, OAuthError
from app.services.social_oauth import oauth_create_or_get_user

router = APIRouter(prefix="/auth", tags=["auth"])

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

oauth = OAuth()

@router.get("/")
async def public(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("main.html", {"request": request})

@router.get("/logout")
async def logout(request: Request):
    """로그아웃"""
    request.session.pop('user', None)
    return RedirectResponse(url='/api/auth')

@router.get("/test-login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/test-signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/verify", response_class=HTMLResponse)
async def verify_page(request: Request):
    """토큰 검증 테스트 페이지"""
    return templates.TemplateResponse("verify_token.html", {"request": request})

@router.post("/verify")
async def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    """토큰 검증 API"""
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "provider": current_user.provider
    }

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
oauth.register(
    name='kakao',
    client_id=settings.KAKAO_CLIENT_ID,
    client_secret=settings.KAKAO_CLIENT_SECRET,
    access_token_url='https://kauth.kakao.com/oauth/token',
    authorize_url='https://kauth.kakao.com/oauth/authorize',
    api_base_url='https://kapi.kakao.com/v2/',
    client_kwargs={
        'scope': 'profile_nickname profile_image account_email',
        'token_endpoint_auth_method': 'client_secret_post',
    }
)
@router.get('/{provider}/login/')
async def login_by_oauth(request: Request, provider: ProviderEnum):
    if provider == ProviderEnum.KAKAO:
        base_url = settings.KAKAO_REDIRECT_URI
    else:
        base_url = settings.GOOGLE_REDIRECT_URI
    # 우리가 만들어줄 callback 주소다. 인증이 완료되면 callback 주소가 호출된다.
    redirect_uri = f'{base_url}/api/auth/{provider}/callback'
    
    # callback 주소를 담아 oauth 제공사들에 맞게 redirect를 요청
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)



@router.get('/{provider}/callback', response_model=Token)
async def callback_by_oauth(request: Request, provider: ProviderEnum, db: Session = Depends(get_db)):
    token = await oauth.create_client(provider).authorize_access_token(request)

    # provider별 user_info 추출
    if provider == ProviderEnum.GOOGLE:
        user_info = {
            "id": token.get("sub") or token["userinfo"].get("sub"),
            "email": token["userinfo"].get("email"),
            "name": token["userinfo"].get("name"),
            "profile_image": token["userinfo"].get("picture"),
        }
    elif provider == ProviderEnum.KAKAO:
        user_info_url = 'https://kapi.kakao.com/v2/user/me'
        user_headers = {"Authorization": f"Bearer {token['access_token']}"}
        async with httpx.AsyncClient() as client:
            user_response = await client.post(user_info_url, headers=user_headers)
            user_response.raise_for_status()
            kakao_data = user_response.json()
            kakao_account = kakao_data.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            user_info = {
                "id": kakao_data.get("id"),
                "email": kakao_account.get("email"),
                "name": profile.get("nickname"),
                "profile_image": profile.get("profile_image_url", None),
            }
    else:
        user_info = {}

    # 서비스 함수 호출 (db 세션 전달)
    user = oauth_create_or_get_user(provider, user_info, db)

    # JWT 토큰 생성
    access_token = create_access_token(str(user.id))
    user_token = Token(
        access_token=access_token,
        token_type='bearer'
    )
    return user_token

