from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.api.deps import SessionDep
from app.models import Category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/{category_id}")
def get_category_name(category_id: int, session: SessionDep):
    # Category 테이블에서 category_id에 해당하는 name 조회
    statement = select(Category.name).where(Category.id == category_id)
    result = session.exec(statement).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"name": result} 