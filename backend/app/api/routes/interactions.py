from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.api.deps import CurrentUser, SessionDep
from app.models import PreferenceEnum, UserNewspaperPreference, Message, UserNewspaperSave, Newspaper
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/interactions", tags=["interactions"])

@router.post("/me/save/{newspaper_id}", response_model=Message)
def save_newspaper_me(newspaper_id: int, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Save a newspaper for the current user.
    """
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail="Newspaper not found")

    existing_save = session.exec(select(UserNewspaperSave).where(
        UserNewspaperSave.user_id == current_user,
        UserNewspaperSave.newspaper_id == newspaper_id
    )).first()

    if existing_save:
        raise HTTPException(status_code=400, detail="Newspaper already saved")

    save_entry = UserNewspaperSave(
        user_id=current_user,
        newspaper_id=newspaper_id,
        save_at=datetime.now(),
        title=newspaper.title,
        summary=newspaper.summary,
        link=newspaper.link
    )
    session.add(save_entry)
    session.commit()
    return Message(message="Newspaper saved successfully")


@router.delete("/me/save/{newspaper_id}", response_model=Message)
def unsave_newspaper_me(newspaper_id: int, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Unsave a newspaper for the current user.
    """
    existing_save = session.exec(select(UserNewspaperSave).where(
        UserNewspaperSave.user_id == current_user,
        UserNewspaperSave.newspaper_id == newspaper_id
    )).first()

    if not existing_save:
        raise HTTPException(status_code=404, detail="Save entry not found")

    session.delete(existing_save)
    session.commit()
    return Message(message="Newspaper unsaved successfully")


@router.post("/me/like/{newspaper_id}", response_model=Message)
def like_newspaper_me(newspaper_id: int, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Handle liking a newspaper by the current user.
    """
    interaction = session.exec(select(UserNewspaperPreference).where(
        UserNewspaperPreference.user_id == current_user,
        UserNewspaperPreference.newspaper_id == newspaper_id
    )).first()

    if interaction:
        if interaction.preference == PreferenceEnum.LIKE:
            interaction.preference = PreferenceEnum.NONE
        else:
            interaction.preference = PreferenceEnum.LIKE
        interaction.update_at = datetime.now()
    else:
        interaction = UserNewspaperPreference(user_id=current_user, newspaper_id=newspaper_id, preference=PreferenceEnum.LIKE, update_at=datetime.now())
        session.add(interaction)

    session.commit()
    return Message(message="Like status updated successfully")


@router.post("/me/dislike/{newspaper_id}", response_model=Message)
def dislike_newspaper_me(newspaper_id: int, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Handle disliking a newspaper by the current user.
    """
    interaction = session.exec(select(UserNewspaperPreference).where(
        UserNewspaperPreference.user_id == current_user,
        UserNewspaperPreference.newspaper_id == newspaper_id
    )).first()

    if interaction:
        if interaction.preference == PreferenceEnum.DISLIKE:
            interaction.preference = PreferenceEnum.NONE
        else:
            interaction.preference = PreferenceEnum.DISLIKE
        interaction.update_at = datetime.now()
    else:
        interaction = UserNewspaperPreference(user_id=current_user, newspaper_id=newspaper_id, preference=PreferenceEnum.DISLIKE, update_at=datetime.now())
        session.add(interaction)

    session.commit()
    return Message(message="Dislike status updated successfully")


@router.post("{user_id}/save/{newspaper_id}", response_model=Message)
def save_newspaper(user_id: UUID, newspaper_id: int, session: SessionDep) -> Message:
    """
    Save a newspaper for a specific user.
    """
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail="Newspaper not found")

    existing_save = session.exec(select(UserNewspaperSave).where(
        UserNewspaperSave.user_id == user_id,
        UserNewspaperSave.newspaper_id == newspaper_id
    )).first()

    if existing_save:
        raise HTTPException(status_code=400, detail="Newspaper already saved")

    save_entry = UserNewspaperSave(
        user_id=user_id,
        newspaper_id=newspaper_id,
        save_at=datetime.now(),
        title=newspaper.title,
        summary=newspaper.summary,
        link=newspaper.link
    )
    session.add(save_entry)
    session.commit()
    return Message(message="Newspaper saved successfully")


@router.delete("/{user_id}/save/{newspaper_id}", response_model=Message)
def unsave_newspaper(user_id: UUID, newspaper_id: int, session: SessionDep) -> Message:
    """
    Unsave a newspaper for a specific user.
    """
    existing_save = session.exec(select(UserNewspaperSave).where(
        UserNewspaperSave.user_id == user_id,
        UserNewspaperSave.newspaper_id == newspaper_id
    )).first()

    if not existing_save:
        raise HTTPException(status_code=404, detail="Save entry not found")

    session.delete(existing_save)
    session.commit()
    return Message(message="Newspaper unsaved successfully")



@router.post("/{user_id}/like/{newspaper_id}", response_model=Message)
def like_newspaper(user_id: UUID, newspaper_id: int, session: SessionDep) -> Message:
    """
    Handle liking a newspaper by a user.
    """
    interaction = session.exec(select(UserNewspaperPreference).where(
        UserNewspaperPreference.user_id == user_id,
        UserNewspaperPreference.newspaper_id == newspaper_id
    )).first()

    if interaction:
        if interaction.preference == PreferenceEnum.LIKE:
            interaction.preference = PreferenceEnum.NONE
        else:
            interaction.preference = PreferenceEnum.LIKE
        interaction.update_at = datetime.now()
    else:
        interaction = UserNewspaperPreference(user_id=user_id, newspaper_id=newspaper_id, preference=PreferenceEnum.LIKE, update_at=datetime.now())
        session.add(interaction)

    session.commit()
    return Message(message="Like status updated successfully")


@router.post("/{user_id}/dislike/{newspaper_id}", response_model=Message)
def dislike_newspaper(user_id: UUID, newspaper_id: int, session: SessionDep) -> Message:
    """
    Handle disliking a newspaper by a user.
    """
    interaction = session.exec(select(UserNewspaperPreference).where(
        UserNewspaperPreference.user_id == user_id,
        UserNewspaperPreference.newspaper_id == newspaper_id
    )).first()

    if interaction:
        if interaction.preference == PreferenceEnum.DISLIKE:
            interaction.preference = PreferenceEnum.NONE
        else:
            interaction.preference = PreferenceEnum.DISLIKE
        interaction.update_at = datetime.now()
    else:
        interaction = UserNewspaperPreference(user_id=user_id, newspaper_id=newspaper_id, preference=PreferenceEnum.DISLIKE, update_at=datetime.now())
        session.add(interaction)

    session.commit()
    return Message(message="Dislike status updated successfully")



