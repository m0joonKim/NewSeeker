from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from app.api.deps import SessionDep
from app.models import Message, NewspaperCategory, Newspaper, Category

router = APIRouter(prefix="/newspapers", tags=["newspapers"])

@router.post("/create", response_model=Newspaper)
def create_newspaper(newspaper: Newspaper, session: SessionDep) -> Newspaper:
    """
    Create a new newspaper entry.
    """
    # ID는 클라이언트가 제공하지 않음
    newspaper.id = None
    session.add(newspaper)
    session.commit()
    session.refresh(newspaper)
    return newspaper

@router.get("/{newspaper_id}/categories", response_model=List[str])
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


@router.post("/{newspaper_id}/categories/toggle", response_model=Message)
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


