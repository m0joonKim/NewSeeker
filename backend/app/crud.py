from datetime import datetime,time
import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate, Alarm, FrequencyEnum, DayOfWeekEnum


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    # Create default alarm for the new user
    default_alarm = Alarm(
        user_id=db_obj.id,
        frequency=FrequencyEnum.NONE,  # Set default frequency
        day_of_week=DayOfWeekEnum.MONDAY,  # Set default day of week
        day_of_month=1,
        receive_time=datetime.combine(datetime.min, time(hour=9, minute=0)),  # Use dummy date
        email_on=False,  # Enable email notifications by default
        kakao_on=False,
        slack_on=False
    )
    session.add(default_alarm)
    session.commit()

    return db_obj



def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


