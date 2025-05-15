from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from app.api.deps import SessionDep, CurrentUser
from app.models import Category, UserCategory, NewspaperCategory, Newspaper, Message, CategoryEnum, User
from typing import List
import uuid

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/{category_id}")
def get_category_name(category_id: int, session: SessionDep):
    # Category 테이블에서 category_id에 해당하는 name 조회
    category = session.exec(select(Category).where(Category.id == category_id)).first()
    
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    
    return {"name": category.name.value}

# @router.get("/user/me/categories", response_model=List[str])
# def get_my_categories(current_user: CurrentUser, session: SessionDep) -> List[str]:
#     """
#     Get preferred categories for the current user as a list of category names.
#     """
#     statement = select(UserCategory).where(UserCategory.user_id == current_user.id)
#     my_categories = session.exec(statement).all()
    
#     # 카테고리 이름 조회
#     category_names = []
#     for uc in my_categories:
#         category = session.exec(select(Category).where(Category.id == uc.category_id)).first()
#         if category:
#             category_names.append(category.name.value)
    
#     return category_names

# @router.post("/user/me/categories/toggle", response_model=Message)
# def toggle_my_category(category_id: int, current_user: CurrentUser, session: SessionDep) -> Message:
#     """
#     Toggle category preference for the current user.
#     """
#     # 카테고리 ID 조회
#     category = session.exec(select(Category).where(Category.id == category_id)).first()
#     if not category:
#         raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    
#     # UserCategory 조회 및 토글
#     statement = select(UserCategory).where(UserCategory.user_id == current_user.id, UserCategory.category_id == category.id)
#     my_category = session.exec(statement).first()
#     if my_category:
#         session.delete(my_category)
#         message = "Category preference removed."
#     else:
#         new_my_category = UserCategory(user_id=current_user.id, category_id=category.id)
#         session.add(new_my_category)
#         message = "Category preference added."
#     session.commit()
#     return Message(message=message)

@router.get("/user/{user_id}/categories", response_model=List[str])
def get_user_categories(user_id: uuid.UUID, session: SessionDep) -> List[str]:
    """
    Get preferred categories for a specific user by user ID.
    """
    # 유저 존재 여부 확인
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    statement = select(UserCategory).where(UserCategory.user_id == user_id)
    user_categories = session.exec(statement).all()
    
    # 카테고리 이름 조회
    category_names = []
    for uc in user_categories:
        category = session.exec(select(Category).where(Category.id == uc.category_id)).first()
        if category:
            category_names.append(category.name.value)
    
    return category_names

@router.get("/user/{user_id}/category_ids", response_model=List[int])
def get_user_category_ids(user_id: uuid.UUID, session: SessionDep) -> List[int]:
    """
    Get preferred category IDs for a specific user by user ID.
    """
    # 유저 존재 여부 확인
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    statement = select(UserCategory).where(UserCategory.user_id == user_id)
    user_categories = session.exec(statement).all()
    
    # 카테고리 ID 조회
    category_ids = [uc.category_id for uc in user_categories]
    
    return category_ids

@router.post("/user/{user_id}/categories/toggle", response_model=Message)
def toggle_user_category(user_id: uuid.UUID, category_id: int, session: SessionDep) -> Message:
    """
    Toggle category preference for a specific user by user ID.
    """
    # 유저 존재 여부 확인
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    # 카테고리 ID 조회
    category = session.exec(select(Category).where(Category.id == category_id)).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    
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

@router.get("/newspaper/{newspaper_id}/categories", response_model=List[str])
def get_newspaper_categories(newspaper_id: int, session: SessionDep) -> List[str]:
    """
    Get categories for a specific newspaper by newspaper ID.
    """
    # 뉴스페이퍼 존재 여부 확인
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail=f"Newspaper with id {newspaper_id} not found")

    statement = select(NewspaperCategory).where(NewspaperCategory.newspaper_id == newspaper_id)
    newspaper_categories = session.exec(statement).all()
    
    # 카테고리 이름 조회
    category_names = []
    for nc in newspaper_categories:
        category = session.exec(select(Category).where(Category.id == nc.category_id)).first()
        if category:
            category_names.append(category.name.value)
    
    return category_names

@router.post("/newspaper/{newspaper_id}/categories/toggle", response_model=Message)
def toggle_newspaper_category(newspaper_id: int, category_id: int, session: SessionDep) -> Message:
    """
    Toggle category for a specific newspaper by newspaper ID.
    """
    # 뉴스페이퍼 존재 여부 확인
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail=f"Newspaper with id {newspaper_id} not found")

    # 카테고리 ID 조회
    category = session.exec(select(Category).where(Category.id == category_id)).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    
    # NewspaperCategory 조회 및 토글
    statement = select(NewspaperCategory).where(NewspaperCategory.newspaper_id == newspaper_id, NewspaperCategory.category_id == category.id)
    newspaper_category = session.exec(statement).first()
    if newspaper_category:
        session.delete(newspaper_category)
        message = "Category preference removed."
    else:
        new_newspaper_category = NewspaperCategory(newspaper_id=newspaper_id, category_id=category.id)
        session.add(new_newspaper_category)
        message = "Category preference added."
    session.commit()
    return Message(message=message)

