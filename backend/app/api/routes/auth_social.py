from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.core.config import settings
from app.models import User, ProviderEnum, UserRegister
from app.core.security import create_access_token, get_password_hash
from app.api.deps import get_db
import httpx
import uuid
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/kakao/login")
async def kakao_login():
    """카카오 로그인 페이지로 리다이렉트"""
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={settings.KAKAO_CLIENT_ID}&redirect_uri={settings.KAKAO_REDIRECT_URI}&response_type=code"
    return RedirectResponse(kakao_auth_url)

@router.get("/kakao/callback")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    """카카오 로그인 콜백 처리 (provider_id로 유저 식별)"""
    token_url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_CLIENT_ID,
        "client_secret": settings.KAKAO_CLIENT_SECRET,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": code
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data, headers=headers)
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="카카오 토큰을 받아오는데 실패했습니다.")
        
        access_token = token_response.json()["access_token"]
        
        # 카카오 사용자 정보 가져오기
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        user_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        user_response = await client.post(user_info_url, headers=user_headers)
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="카카오 사용자 정보를 가져오는데 실패했습니다.")
        
        user_info = user_response.json()
        kakao_id = str(user_info["id"])
        kakao_account = user_info.get("kakao_account", {})
        email = kakao_account.get("email")
        profile = kakao_account.get("profile", {})
        nickname = profile.get("nickname", "")
        profile_image = profile.get("profile_image_url")

        # provider_id(카카오 고유 ID)로 유저를 우선 조회
        user = db.exec(
            select(User).where(
                (User.provider == ProviderEnum.KAKAO) & (User.provider_id == kakao_id)
            )
        ).first()

        # 없으면 이메일로도 한 번 더 조회(이전 가입자 호환)
        if not user:
            user = User(
                email=None,
                provider=ProviderEnum.KAKAO,
                provider_id=kakao_id,
                full_name=nickname,
                profile_image=profile_image
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # JWT 토큰 생성
        jwt_token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # 프론트엔드로 리다이렉트 (토큰 포함, 이메일이 더미인지도 전달)
        return RedirectResponse(
            f"{settings.FRONTEND_HOST}/auth/callback?token={jwt_token}"
            # "http://localhost:8000/api/auth/kakao/callback"
        )


