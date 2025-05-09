from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.api.deps import SessionDep, CurrentUser
from app.models import Category, UserCategory, NewspaperCategory, Newspaper
from typing import List
import uuid
from app.models import Message

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/{category_id}")
def get_category_name(category_id: int, session: SessionDep):
    # Category 테이블에서 category_id에 해당하는 name 조회
    statement = select(Category.name).where(Category.id == category_id)
    result = session.exec(statement).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"name": result}

@router.get("/user/me/categories", response_model=List[str])
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

@router.post("/user/me/categories/toggle", response_model=Message)
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


@router.get("/user/{user_id}/categories", response_model=List[str])
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

@router.post("/user/{user_id}/categories/toggle", response_model=Message)
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


@router.get("/newspaper/{newspaper_id}/categories", response_model=List[str])
def get_newspaper_categories(newspaper_id: int, session: SessionDep) -> List[str]:
    """
    Get categories for a specific newspaper by newspaper ID.
    """
    statement = select(NewspaperCategory).where(NewspaperCategory.newspaper_id == newspaper_id)
    newspaper_categories = session.exec(statement).all()
    
    # 카테고리 이름 조회
    category_names = []
    for nc in newspaper_categories:
        category_statement = select(Category.name).where(Category.id == nc.category_id)
        category_name = session.exec(category_statement).first()
        if category_name:
            category_names.append(category_name)
    
    return category_names


@router.post("/newspaper/{newspaper_id}/categories/toggle", response_model=Message)
def toggle_newspaper_category(newspaper_id: int, category_name: str, session: SessionDep) -> Message:
    """
    Toggle category for a specific newspaper by newspaper ID.
    """
    # 카테고리 ID 조회
    category = session.exec(select(Category).where(Category.name == category_name)).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category name.")
    
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