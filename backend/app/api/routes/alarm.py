from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.api.deps import SessionDep, CurrentUser
from app.models import Alarm, FrequencyEnum, Message, DayOfWeekEnum, User
import uuid
from datetime import time

router = APIRouter(prefix="/alarms", tags=["alarms"])



# @router.patch("/{user_id}/email_on", response_model=Message)
# def toggle_user_email_on(user_id: uuid.UUID, session: SessionDep) -> Message:
#     """
#     Toggle email_on for a specific user's alarm by user ID.
#     """
#     # 유저 존재 여부 확인
#     user_exists = session.exec(select(User).where(User.id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     # 알람 존재 여부 확인
#     alarm = session.exec(select(Alarm).where(Alarm.user_id == user_id)).first()
#     if not alarm:
#         raise HTTPException(status_code=404, detail="Alarm not found")
#     alarm.email_on = not alarm.email_on
#     session.add(alarm)
#     session.commit()
#     if alarm.email_on:
#         return Message(message="Email notification toggled successfully : Email on")
#     else:
#         return Message(message="Email notification toggled successfully : Email off")


# @router.patch("/{user_id}/kakao_on", response_model=Message)
# def toggle_user_kakao_on(user_id: uuid.UUID, session: SessionDep) -> Message:
#     """
#     Toggle kakao_on for a specific user's alarm by user ID.
#     """
#     user_exists = session.exec(select(User).where(User.id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     alarm = session.exec(select(Alarm).where(Alarm.user_id == user_id)).first()
#     if not alarm:
#         raise HTTPException(status_code=404, detail="Alarm not found")
#     alarm.kakao_on = not alarm.kakao_on
#     session.add(alarm)
#     session.commit()
#     if alarm.kakao_on:
#         return Message(message="Kakao notification toggled successfully : Kakao on")
#     else:
#         return Message(message="Kakao notification toggled successfully : Kakao off")


# @router.patch("/{user_id}/slack_on", response_model=Message)
# def toggle_user_slack_on(user_id: uuid.UUID, session: SessionDep) -> Message:
#     """
#     Toggle slack_on for a specific user's alarm by user ID.
#     """
#     user_exists = session.exec(select(User).where(User.id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     alarm = session.exec(select(Alarm).where(Alarm.user_id == user_id)).first()
#     if not alarm:
#         raise HTTPException(status_code=404, detail="Alarm not found")
#     alarm.slack_on = not alarm.slack_on
#     session.add(alarm)
#     session.commit()
#     if alarm.slack_on:
#         return Message(message="Slack notification toggled successfully : Slack on")
#     else:
#         return Message(message="Slack notification toggled successfully : Slack off")


# @router.patch("/{user_id}/frequency", response_model=Message)
# def set_user_alarm_frequency(user_id: uuid.UUID, frequency: FrequencyEnum, session: SessionDep) -> Message:
#     """
#     Set alarm frequency for a specific user by user ID.
#     """
#     user_exists = session.exec(select(User).where(User.id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     alarm = session.exec(select(Alarm).where(Alarm.user_id == user_id)).first()
#     if not alarm:
#         raise HTTPException(status_code=404, detail="Alarm not found")
#     alarm.frequency = frequency
#     session.add(alarm)
#     session.commit()
#     return Message(message="Alarm frequency updated successfully")




# @router.patch("/{user_id}/day_of_month", response_model=Message)
# def set_user_alarm_day_of_month(user_id: uuid.UUID, day_of_month: int, session: SessionDep) -> Message:
#     """
#     Set alarm day of the month for a specific user by user ID.
#     """
#     user_exists = session.exec(select(User).where(User.id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     if not 1 <= day_of_month <= 31:
#         raise HTTPException(status_code=400, detail="Invalid day of month")
#     alarm = session.exec(select(Alarm).where(Alarm.user_id == user_id)).first()
#     if not alarm:
#         raise HTTPException(status_code=404, detail="Alarm not found")
#     alarm.day_of_month = day_of_month
#     session.add(alarm)
#     session.commit()
#     return Message(message="Alarm day of month updated successfully")


# @router.patch("/{user_id}/day_of_week", response_model=Message)
# def set_user_alarm_day_of_week(user_id: uuid.UUID, day_of_week: DayOfWeekEnum, session: SessionDep) -> Message:
#     """
#     Set alarm day of the week for a specific user by user ID.
#     """
#     user_exists = session.exec(select(User).where(User.id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     alarm = session.exec(select(Alarm).where(Alarm.user_id == user_id)).first()
#     if not alarm:
#         raise HTTPException(status_code=404, detail="Alarm not found")
#     alarm.day_of_week = day_of_week
#     session.add(alarm)
#     session.commit()
#     return Message(message="Alarm day of week updated successfully")


# @router.patch("/{user_id}/receive_time", response_model=Message)
# def set_user_alarm_receive_time(user_id: uuid.UUID, receive_time: time, session: SessionDep) -> Message:
#     """
#     Set alarm receive time for a specific user by user ID.
#     """
#     user_exists = session.exec(select(User).where(User.id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     alarm = session.exec(select(Alarm).where(Alarm.user_id == user_id)).first()
#     if not alarm:
#         raise HTTPException(status_code=404, detail="Alarm not found")
#     alarm.receive_time = receive_time
#     session.add(alarm)
#     session.commit()
#     return Message(message="Alarm receive time updated successfully")


# @router.get("/{user_id}", response_model=Alarm)
# def get_user_alarm(user_id: uuid.UUID, session: SessionDep) -> Alarm:
#     """
#     Retrieve alarm information for a specific user by user ID.
#     """
#     # 유저 존재 여부 확인
#     user_exists = session.exec(select(User).where(User.id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     # 알람 정보 가져오기
#     alarm = session.exec(select(Alarm).where(Alarm.user_id == user_id)).first()
#     if not alarm:
#         raise HTTPException(status_code=404, detail="Alarm not found")
#     return alarm


@router.patch("/me/email_on", response_model=Message)
def toggle_my_email_on(current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Toggle email_on for the current user's alarm.
    """
    alarm = session.exec(select(Alarm).where(Alarm.user_id == current_user.id)).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    alarm.email_on = not alarm.email_on
    session.add(alarm)
    session.commit()
    if alarm.email_on:
        return Message(message="Email notification toggled successfully : Email on")
    else:
        return Message(message="Email notification toggled successfully : Email off")


@router.patch("/me/kakao_on", response_model=Message)
def toggle_my_kakao_on(current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Toggle kakao_on for the current user's alarm.
    """
    alarm = session.exec(select(Alarm).where(Alarm.user_id == current_user.id)).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    alarm.kakao_on = not alarm.kakao_on
    session.add(alarm)
    session.commit()
    if alarm.kakao_on:
        return Message(message="Kakao notification toggled successfully : Kakao on")
    else:
        return Message(message="Kakao notification toggled successfully : Kakao off")


@router.patch("/me/slack_on", response_model=Message)
def toggle_my_slack_on(current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Toggle slack_on for the current user's alarm.
    """
    alarm = session.exec(select(Alarm).where(Alarm.user_id == current_user.id)).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    alarm.slack_on = not alarm.slack_on
    session.add(alarm)
    session.commit()
    if alarm.slack_on:
        return Message(message="Slack notification toggled successfully : Slack on")
    else:
        return Message(message="Slack notification toggled successfully : Slack off")


@router.patch("/me/frequency", response_model=Message)
def set_my_alarm_frequency(frequency: FrequencyEnum, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Set alarm frequency for the current user.
    """
    alarm = session.exec(select(Alarm).where(Alarm.user_id == current_user.id)).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    alarm.frequency = frequency
    session.add(alarm)
    session.commit()
    return Message(message="Alarm frequency updated successfully")


@router.patch("/me/day_of_month", response_model=Message)
def set_my_alarm_day_of_month(day_of_month: int, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Set alarm day of the month for the current user.
    """
    if not 1 <= day_of_month <= 31:
        raise HTTPException(status_code=400, detail="Invalid day of month")
    alarm = session.exec(select(Alarm).where(Alarm.user_id == current_user.id)).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    alarm.day_of_month = day_of_month
    session.add(alarm)
    session.commit()
    return Message(message="Alarm day of month updated successfully")


@router.patch("/me/day_of_week", response_model=Message)
def set_my_alarm_day_of_week(day_of_week: DayOfWeekEnum, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Set alarm day of the week for the current user.
    """
    alarm = session.exec(select(Alarm).where(Alarm.user_id == current_user.id)).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    alarm.day_of_week = day_of_week
    session.add(alarm)
    session.commit()
    return Message(message="Alarm day of week updated successfully")


@router.patch("/me/receive_time", response_model=Message)
def set_my_alarm_receive_time(receive_time: time, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Set alarm receive time for the current user.
    """
    alarm = session.exec(select(Alarm).where(Alarm.user_id == current_user.id)).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    alarm.receive_time = receive_time
    session.add(alarm)
    session.commit()
    return Message(message="Alarm receive time updated successfully")


@router.get("/me", response_model=Alarm)
def get_my_alarm(current_user: CurrentUser, session: SessionDep) -> Alarm:
    """
    Retrieve alarm information for the current user.
    """
    alarm = session.exec(select(Alarm).where(Alarm.user_id == current_user.id)).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return alarm


