import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import delete
from app.api.routes.category import get_newspaper_categories
from sqlmodel import select
from typing import List, Optional
from app.api.deps import SessionDep
from app.models import Message, NewsPaperType, NewspaperCategory, Newspaper, Category, UserNewspaperPreference, UserCategory
from app.api.deps import CurrentUser


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# @router.get("/user-categories/{user_id}", response_model=List[dict])
# def get_user_newspapers_by_category(
#     user_id: uuid.UUID, 
#     session: SessionDep, 
#     type: Optional[NewsPaperType] = None
# ) -> List[dict]:
#     """
#     Get a list of newspapers and papers based on user's categories.
#     Optionally filter by type: 'news' or 'paper'.
#     Include category information for each newspaper.
#     """
#     # 유저 존재 여부 확인
#     user_exists = session.exec(select(UserCategory).where(UserCategory.user_id == user_id)).first()
#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     # 유저의 카테고리 ID 목록 가져오기
#     user_categories = session.exec(
#         select(UserCategory.category_id).where(UserCategory.user_id == user_id)
#     ).all()
    
#     if not user_categories:
#         raise HTTPException(status_code=404, detail="User categories not found")

#     # 중복 제거
#     unique_category_ids = set(user_categories)
    
#     # 해당 카테고리의 뉴스 및 논문 가져오기
#     statement = select(Newspaper).where(Newspaper.newspaper_categories.any(
#         NewspaperCategory.category_id.in_(unique_category_ids)
#     )).order_by(Newspaper.date.desc())
    
#     if type:
#         statement = statement.where(Newspaper.type == type)
    
#     newspapers = session.exec(statement).all()
    
#     if not newspapers:
#         raise HTTPException(status_code=404, detail="No newspapers found for the given categories")

#     # 각 뉴스페이퍼에 카테고리 정보 추가
#     result = []
#     for newspaper in newspapers:
#         categories = get_newspaper_categories(newspaper.id, session)
#         result.append({
#             "newspaper": newspaper,
#             "categories": categories
#         })
    
#     return result


@router.get("/", response_model=List[dict])
def get_all_newspapers(request: Request, session: SessionDep, type: Optional[NewsPaperType] = None):
    """
    Get a list of all newspapers.
    Optionally filter by type: 'news', 'paper', or None for all types.
    """
    # 쿠키 정보 로그 출력
    print("Cookies:", request.cookies)

    statement = select(Newspaper).order_by(Newspaper.date.desc())
    if type:
        statement = statement.where(Newspaper.type == type)
    newspapers = session.exec(statement).all()
    result = []
    for newspaper in newspapers:
        categories = get_newspaper_categories(newspaper.id, session)
        result.append({
            "newspaper": newspaper,
            "categories": categories
        })
    return result


@router.get("/me/user-categories", response_model=List[dict])
def get_my_newspapers_by_category(
    request: Request,
    current_user: CurrentUser, 
    session: SessionDep, 
    type: Optional[NewsPaperType] = None
) -> List[dict]:
    """
    Get a list of newspapers and papers based on current user's categories.
    Optionally filter by type: 'news' or 'paper'.
    Include category information for each newspaper.
    """
    # 쿠키 정보 로그 출력
    print("Cookies:", request.cookies)

    # 유저의 카테고리 ID 목록 가져오기
    user_categories = session.exec(
        select(UserCategory.category_id).where(UserCategory.user_id == current_user.id)
    ).all()
    

    # 중복 제거
    unique_category_ids = set(user_categories)
    
    # 해당 카테고리의 뉴스 및 논문 가져오기
    statement = select(Newspaper).where(Newspaper.newspaper_categories.any(
        NewspaperCategory.category_id.in_(unique_category_ids)
    )).order_by(Newspaper.date.desc())
    
    if type:
        statement = statement.where(Newspaper.type == type)
    
    newspapers = session.exec(statement).all()
    

    # 각 뉴스페이퍼에 카테고리 정보 추가
    result = []
    for newspaper in newspapers:
        categories = get_newspaper_categories(newspaper.id, session)
        result.append({
            "newspaper": newspaper,
            "categories": categories
        })
    
    return result