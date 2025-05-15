from fastapi import APIRouter, Request, Depends, HTTPException
from sqlmodel import Session, select
from app.models import User, ProviderEnum, Token, Alarm, FrequencyEnum, DayOfWeekEnum
from app.core.security import create_access_token
from app.api.deps import get_db
from datetime import datetime, time

# 소셜 OAuth 인증 후 사용자 생성/조회 함수
def oauth_create_or_get_user(provider: str, user_info: dict, db: Session) -> User:
    provider_enum = ProviderEnum(provider.lower())
    provider_id = str(user_info.get("sub") or user_info.get("id"))
    user = db.exec(
        select(User).where(
            (User.provider == provider_enum) & (User.provider_id == provider_id)
        )
    ).first()
    if not user:
        # 이메일 중복 체크
        email = user_info.get("email")
        print(email)
        if email:
            existing_user = db.exec(
                select(User).where(User.email == email)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="이미 가입한 이메일입니다."
                )
        user = User(
            provider=provider_enum,
            provider_id=provider_id,
            email=email,
            full_name=user_info.get("name") or user_info.get("nickname"),
            profile_image=user_info.get("picture") or user_info.get("profile_image_url"),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create default alarm for the new user
        default_alarm = Alarm(
            user_id=user.id,
            frequency=FrequencyEnum.NONE,  # Set default frequency
            day_of_week=DayOfWeekEnum.MONDAY,  # Set default day of week
            day_of_month=1,
            receive_time=datetime.combine(datetime.min, time(hour=9, minute=0)),  # Use dummy date
            email_on=False,  # Enable email notifications by default
            kakao_on=False,
            slack_on=False
        )
        db.add(default_alarm)
        db.commit()
    return user

