import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    UserCategory,
    CategoryEnum,
    Category,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")

#==============================================

@router.get("/{user_id}/categories", response_model=List[str])
def get_user_categories(user_id: uuid.UUID, session: SessionDep) -> List[str]:
    """
    Get preferred categories for a specific user by user ID.
    """
    statement = select(UserCategory).where(UserCategory.user_id == user_id)
    user_categories = session.exec(statement).all()
    
    # 카테고리 이름 조회
    category_names = []
    for uc in user_categories:
        category_statement = select(Category.name).where(Category.id == uc.category_id)
        category_name = session.exec(category_statement).first()
        if category_name:
            category_names.append(category_name)
    
    return category_names


@router.get("/me/categories", response_model=List[str])
def get_my_categories(current_user: CurrentUser, session: SessionDep) -> List[str]:
    """
    Get preferred categories for the current user as a list of category names.
    """
    statement = select(UserCategory).where(UserCategory.user_id == current_user.id)
    my_categories = session.exec(statement).all()
    
    # 카테고리 이름 조회
    category_names = []
    for uc in my_categories:
        category_statement = select(Category.name).where(Category.id == uc.category_id)
        category_name = session.exec(category_statement).first()
        if category_name:
            category_names.append(category_name)
    
    return category_names


@router.post("/{user_id}/categories/toggle", response_model=Message)
def toggle_user_category(user_id: uuid.UUID, category_name: str, session: SessionDep) -> Message:
    """
    Toggle category preference for a specific user by user ID.
    """
    # 카테고리 ID 조회
    category = session.exec(select(Category).where(Category.name == category_name)).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category name.")
    
    # UserCategory 조회 및 토글
    statement = select(UserCategory).where(UserCategory.user_id == user_id, UserCategory.category_id == category.id)
    user_category = session.exec(statement).first()
    if user_category:
        session.delete(user_category)
        message = "Category preference removed."
    else:
        new_user_category = UserCategory(user_id=user_id, category_id=category.id)
        session.add(new_user_category)
        message = "Category preference added."
    session.commit()
    return Message(message=message)


@router.post("/me/categories/toggle", response_model=Message)
def toggle_my_category(category_name: str, current_user: CurrentUser, session: SessionDep) -> Message:
    """
    Toggle category preference for the current user.
    """
    # 카테고리 ID 조회
    category = session.exec(select(Category).where(Category.name == category_name)).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category name.")
    
    # UserCategory 조회 및 토글
    statement = select(UserCategory).where(UserCategory.user_id == current_user.id, UserCategory.category_id == category.id)
    my_category = session.exec(statement).first()
    if my_category:
        session.delete(my_category)
        message = "Category preference removed."
    else:
        new_my_category = UserCategory(user_id=current_user.id, category_id=category.id)
        session.add(new_my_category)
        message = "Category preference added."
    session.commit()
    return Message(message=message)

