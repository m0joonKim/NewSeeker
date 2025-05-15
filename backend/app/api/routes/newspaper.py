from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlmodel import select
from typing import List, Optional
from app.api.deps import SessionDep
from app.models import Message, NewsPaperType, NewspaperCategory, Newspaper, Category, UserNewspaperPreference

router = APIRouter(prefix="/newspapers", tags=["newspapers"])

@router.get("/", response_model=List[Newspaper])
def get_all_newspapers(session: SessionDep, type: Optional[NewsPaperType] = None) -> List[Newspaper]:
    """
    Get a list of all newspapers.
    Optionally filter by type: 'news', 'paper', or None for all types.
    """
    statement = select(Newspaper)
    if type:
        statement = statement.where(Newspaper.type == type)
    newspapers = session.exec(statement).all()
    return newspapers

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

@router.get("/{newspaper_id}", response_model=Newspaper)
def get_newspaper_by_id(newspaper_id: int, session: SessionDep) -> Newspaper:
    """
    Get a newspaper by its ID.
    """
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail="Newspaper not found")
    return newspaper

@router.put("/{newspaper_id}", response_model=Newspaper)
def update_newspaper(newspaper_id: int, updated_data: Newspaper, session: SessionDep) -> Newspaper:
    """
    Update a newspaper by its ID.
    """
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail="Newspaper not found")
    updated_data.id = newspaper_id  # Ensure the ID remains the same
    session.merge(updated_data)
    session.commit()
    session.refresh(updated_data)
    return updated_data

@router.delete("/{newspaper_id}", response_model=Message)
def delete_newspaper(newspaper_id: int, session: SessionDep) -> Message:
    """
    Delete a newspaper by its ID.
    """
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail="Newspaper not found")
    session.delete(newspaper)
    session.commit()
    return Message(message="Newspaper deleted successfully")

@router.get("/by_category/{category_id}")
def get_newspapers_by_category(category_id: int, session: SessionDep, type: Optional[NewsPaperType] = None):
    """
    Get a list of newspapers that belong to a specific category by category name.
    Optionally filter by type: 'news', 'paper', or None for all types.
    """
    # 카테고리 존재 여부 확인
    category = session.exec(select(Category).where(Category.id == category_id)).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    # 해당 카테고리의 뉴스페이퍼 ID 목록 조회
    newspaper_ids = session.exec(
        select(NewspaperCategory.newspaper_id)
        .where(NewspaperCategory.category_id == category_id)
    ).all()
    if not newspaper_ids:
        return []
    # 뉴스페이퍼 상세 정보 조회
    statement = select(Newspaper).where(Newspaper.id.in_(newspaper_ids))
    if type:
        statement = statement.where(Newspaper.type == type)
    newspapers = session.exec(statement.order_by(Newspaper.date.desc())).all()
    
    return newspapers


@router.patch("/{newspaper_id}/increment_hits", response_model=Message)
def increment_newspaper_hits(newspaper_id: int, session: SessionDep) -> Message:
    """
    Increment the hits of a newspaper by 1 when accessed by a user.
    """
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail="Newspaper not found")
    newspaper.hits += 1
    session.add(newspaper)
    session.commit()
    return Message(message="Newspaper hits incremented successfully")

