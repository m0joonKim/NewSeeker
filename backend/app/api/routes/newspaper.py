from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlmodel import select
from typing import List
from app.api.deps import SessionDep
from app.models import Message, NewspaperCategory, Newspaper, Category, UserNewspaperPreference

router = APIRouter(prefix="/newspapers", tags=["newspapers"])

@router.get("/", response_model=List[Newspaper])
def get_all_newspapers(session: SessionDep, type: str = None) -> List[Newspaper]:
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
    Delete a newspaper by its ID, ensuring related NewspaperCategory entries are deleted first.
    """
    # Delete related NewspaperCategory entries first
    session.exec(delete(NewspaperCategory).where(NewspaperCategory.newspaper_id == newspaper_id))
    session.exec(delete(UserNewspaperPreference).where(UserNewspaperPreference.newspaper_id == newspaper_id))
    newspaper = session.exec(select(Newspaper).where(Newspaper.id == newspaper_id)).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail="Newspaper not found")
    session.delete(newspaper)
    session.commit()
    return Message(message="Newspaper and related categories deleted successfully")


@router.get("/{category_name}", response_model=List[Newspaper])
def get_newspapers_by_category_name(category_name: str, session: SessionDep, type: str = None) -> List[Newspaper]:
    """
    Get a list of newspapers that belong to a specific category by category name.
    Optionally filter by type: 'news', 'paper', or None for all types.
    """
    category = session.exec(select(Category).where(Category.name == category_name)).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    statement = select(Newspaper).join(NewspaperCategory).where(NewspaperCategory.category_id == category.id)
    if type:
        statement = statement.where(Newspaper.type == type)
    newspapers = session.exec(statement).all()
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

