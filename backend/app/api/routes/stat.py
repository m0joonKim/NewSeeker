from fastapi import APIRouter, HTTPException
from app.api.routes.category import get_newspaper_categories
from sqlmodel import select, func
from app.api.deps import SessionDep
from app.models import Category, UserCategory, NewspaperCategory, Newspaper, UserNewspaperSave, UserNewspaperPreference, PreferenceEnum, NewsPaperType, User
from typing import Dict, List, Optional

router = APIRouter(prefix="/stat", tags=["statistics"])



@router.get("/top-{k}-hits/{category_id}", response_model=List[dict])
def get_top_hits_by_category(
    category_id: int,  # 단일 카테고리 ID
    k: int, 
    session: SessionDep, 
    type: Optional[NewsPaperType] = None
) -> List[dict]:
    """
    Get top k newspapers with the highest hits from the given category.
    Optionally filter by type: 'news' or 'paper'.
    """
    # 카테고리 존재 여부 확인
    category = session.exec(select(Category).where(Category.id == category_id)).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # 해당 카테고리의 뉴스 및 논문 가져오기
    statement = select(Newspaper).where(Newspaper.newspaper_categories.any(
        NewspaperCategory.category_id == category_id
    )).order_by(Newspaper.hits.desc(), Newspaper.date.desc()).limit(k)
    
    if type:
        statement = statement.where(Newspaper.type == type)
    
    newspapers = session.exec(statement).all()
    if not newspapers:
        raise HTTPException(status_code=404, detail="No newspapers found for the given conditions")
    # 각 뉴스페이퍼에 카테고리 정보 추가
    result = []
    for newspaper in newspapers:
        categories = get_newspaper_categories(newspaper.id, session)
        result.append({
            "newspaper": newspaper,
            "categories": categories
        })
    
    return result


@router.get("/total-users")
def get_total_users(session: SessionDep) -> Dict[str, int]:
    """
    총 유저 수를 반환합니다.
    """
    user_count = session.exec(select(func.count(User.id))).first()
    return {"total_users": user_count or 0}


@router.get("/total-news")
def get_total_news(session: SessionDep) -> Dict[str, int]:
    """
    총 뉴스 수를 반환합니다.
    """
    news_count = session.exec(
        select(func.count(Newspaper.id)).where(Newspaper.type == NewsPaperType.NEWS)
    ).first()
    return {"total_news": news_count or 0}


@router.get("/total-papers")
def get_total_papers(session: SessionDep) -> Dict[str, int]:
    """
    총 논문 수를 반환합니다.
    """
    paper_count = session.exec(
        select(func.count(Newspaper.id)).where(Newspaper.type == NewsPaperType.PAPER)
    ).first()
    return {"total_papers": paper_count or 0}


@router.get("/category-stats")
def get_category_stats(session: SessionDep) -> List[Dict]:
    """
    모든 카테고리에 대해 뉴스, 논문, 선호 유저 수 및 hits 총합을 반환합니다.
    """
    categories = session.exec(select(Category)).all()
    result = []
    for category in categories:
        news_count = session.exec(
            select(func.count(NewspaperCategory.newspaper_id))
            .join(Newspaper, NewspaperCategory.newspaper_id == Newspaper.id)
            .where(
                NewspaperCategory.category_id == category.id,
                Newspaper.type == NewsPaperType.NEWS
            )
        ).first()

        paper_count = session.exec(
            select(func.count(NewspaperCategory.newspaper_id))
            .join(Newspaper, NewspaperCategory.newspaper_id == Newspaper.id)
            .where(
                NewspaperCategory.category_id == category.id,
                Newspaper.type == NewsPaperType.PAPER
            )
        ).first()

        user_count = session.exec(
            select(func.count(UserCategory.user_id))
            .where(UserCategory.category_id == category.id)
        ).first()

        total_hits = session.exec(
            select(func.sum(Newspaper.hits))
            .join(NewspaperCategory, Newspaper.id == NewspaperCategory.newspaper_id)
            .where(NewspaperCategory.category_id == category.id)
        ).first()

        result.append({
            "category_name": category.name.value,
            "news_count": news_count or 0,
            "paper_count": paper_count or 0,
            "user_count": user_count or 0,
            "total_hits": total_hits or 0
        })
    return result



# @router.get("/by_category/{category_id}")
# def get_category_stats(category_id: int, session: SessionDep):
#     """
#     특정 카테고리의 통계 정보를 반환합니다:
#     - 선호하는 유저 수
#     - 관련 논문 수 (NewspaperCategory에서 type이 'paper'인 것)
#     - 관련 뉴스 수 (NewspaperCategory에서 type이 'news'인 것)
#     - 논문+뉴스 총 수
#     - 저장된 수
#     - 좋아요 수
#     - 싫어요 수
#     """
#     # 카테고리 조회
#     category = session.exec(select(Category).where(Category.id == category_id)).first()
#     if not category:
#         raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    
#     # 선호하는 유저 수
#     user_count = session.exec(
#         select(func.count(UserCategory.user_id))
#         .where(UserCategory.category_id == category.id)
#     ).first()
    
#     # 관련 논문 수 (type이 'paper'인 것)
#     paper_count = session.exec(
#         select(func.count(NewspaperCategory.newspaper_id))
#         .join(Newspaper, NewspaperCategory.newspaper_id == Newspaper.id)
#         .where(
#             NewspaperCategory.category_id == category.id,
#             Newspaper.type == 'paper'
#         )
#     ).first()
    
#     # 관련 뉴스 수 (type이 'news'인 것)
#     news_count = session.exec(
#         select(func.count(NewspaperCategory.newspaper_id))
#         .join(Newspaper, NewspaperCategory.newspaper_id == Newspaper.id)
#         .where(
#             NewspaperCategory.category_id == category.id,
#             Newspaper.type == 'news'
#         )
#     ).first()
    
#     # 총 콘텐츠 수
#     total_content = paper_count + news_count

#     # 저장된 수
#     save_count = session.exec(
#         select(func.count(UserNewspaperSave.user_id))
#         .join(Newspaper, UserNewspaperSave.newspaper_id == Newspaper.id)
#         .join(NewspaperCategory, Newspaper.id == NewspaperCategory.newspaper_id)
#         .where(NewspaperCategory.category_id == category.id)
#     ).first()

#     # 좋아요 수
#     like_count = session.exec(
#         select(func.count(UserNewspaperPreference.user_id))
#         .join(Newspaper, UserNewspaperPreference.newspaper_id == Newspaper.id)
#         .join(NewspaperCategory, Newspaper.id == NewspaperCategory.newspaper_id)
#         .where(
#             NewspaperCategory.category_id == category.id,
#             UserNewspaperPreference.preference == PreferenceEnum.LIKE
#         )
#     ).first()

#     # 싫어요 수
#     unlike_count = session.exec(
#         select(func.count(UserNewspaperPreference.user_id))
#         .join(Newspaper, UserNewspaperPreference.newspaper_id == Newspaper.id)
#         .join(NewspaperCategory, Newspaper.id == NewspaperCategory.newspaper_id)
#         .where(
#             NewspaperCategory.category_id == category.id,
#             UserNewspaperPreference.preference == PreferenceEnum.DISLIKE
#         )
#     ).first()
    
#     return {
#         "category_id": category.id,
#         "category_name": category.name.value,
#         "user_count": user_count or 0,
#         "paper_count": paper_count or 0,
#         "news_count": news_count or 0,
#         "total_content": total_content,
#         "save_count": save_count or 0,
#         "like_count": like_count or 0,
#         "unlike_count": unlike_count or 0
#     }

# @router.get("/highlights/save/{limit}/{category_id}")
# def get_category_highlights_by_saves(category_id: int, limit: int, session: SessionDep, type: NewsPaperType = None) -> Dict:
#     """
#     특정 카테고리에서 저장(saves)이 많은 상위 N개의 뉴스페이퍼를 반환합니다.
#     각 뉴스페이퍼별로 저장 개수만 포함합니다.
#     """
#     # 카테고리 존재 여부 확인
#     category = session.exec(select(Category).where(Category.id == category_id)).first()
#     if not category:
#         raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")

#     # 1. NewspaperCategory에서 해당 category_id를 가진 모든 newspaper_id 조회 (중복 제거)
#     newspaper_ids = session.exec(
#         select(NewspaperCategory.newspaper_id)
#         .where(NewspaperCategory.category_id == category_id)
#         .distinct()
#     ).all()
    
#     if type:
#         # type 필터링이 있는 경우, 해당 type의 newspaper_id만 필터링
#         newspaper_ids = session.exec(
#             select(NewspaperCategory.newspaper_id)
#             .join(Newspaper, NewspaperCategory.newspaper_id == Newspaper.id)
#             .where(
#                 NewspaperCategory.category_id == category_id,
#                 Newspaper.type == type
#             )
#             .distinct()
#         ).all()
    
#     # 2. 각 newspaper_id에 대해 저장 수 계산
#     newspaper_stats = session.exec(
#         select(
#             Newspaper,
#             func.count(UserNewspaperSave.user_id).label('save_count')
#         )
#         .outerjoin(UserNewspaperSave, Newspaper.id == UserNewspaperSave.newspaper_id)
#         .where(Newspaper.id.in_(newspaper_ids))
#         .group_by(Newspaper.id)
#         .order_by(func.count(UserNewspaperSave.user_id).desc())
#         .limit(limit)
#     ).all()
    
#     return {
#         "newspapers": [
#             {
#                 "newspaper": n.Newspaper,
#                 "save_count": n.save_count or 0
#             }
#             for n in newspaper_stats
#         ]
#     }

# @router.get("/highlights/like/{limit}/{category_id}")
# def get_category_highlights_by_likes(category_id: int, limit: int, session: SessionDep, type: NewsPaperType = None) -> Dict:
#     """
#     특정 카테고리에서 좋아요(likes)가 많은 상위 N개의 뉴스페이퍼를 반환합니다.
#     각 뉴스페이퍼별로 좋아요 개수만 포함합니다.
#     """
#     # 카테고리 존재 여부 확인
#     category = session.exec(select(Category).where(Category.id == category_id)).first()
#     if not category:
#         raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")

#     # 1. NewspaperCategory에서 해당 category_id를 가진 모든 newspaper_id 조회 (중복 제거)
#     newspaper_ids = session.exec(
#         select(NewspaperCategory.newspaper_id)
#         .where(NewspaperCategory.category_id == category_id)
#         .distinct()
#     ).all()
    
#     if type:
#         # type 필터링이 있는 경우, 해당 type의 newspaper_id만 필터링
#         newspaper_ids = session.exec(
#             select(NewspaperCategory.newspaper_id)
#             .join(Newspaper, NewspaperCategory.newspaper_id == Newspaper.id)
#             .where(
#                 NewspaperCategory.category_id == category_id,
#                 Newspaper.type == type
#             )
#             .distinct()
#         ).all()
    
#     # 2. 각 newspaper_id에 대해 좋아요 수 계산
#     newspaper_stats = session.exec(
#         select(
#             Newspaper,
#             func.count(UserNewspaperPreference.user_id).label('like_count')
#         )
#         .outerjoin(UserNewspaperPreference, Newspaper.id == UserNewspaperPreference.newspaper_id)
#         .where(
#             Newspaper.id.in_(newspaper_ids),
#             UserNewspaperPreference.preference == PreferenceEnum.LIKE
#         )
#         .group_by(Newspaper.id)
#         .order_by(func.count(UserNewspaperPreference.user_id).desc())
#         .limit(limit)
#     ).all()
    
#     return {
#         "newspapers": [
#             {
#                 "newspaper": n.Newspaper,
#                 "like_count": n.like_count or 0
#             }
#             for n in newspaper_stats
#         ]
#     }

# @router.get("/highlights/dislike/{limit}/{category_id}")
# def get_category_highlights_by_dislikes(category_id: int, limit: int, session: SessionDep, type: NewsPaperType = None) -> Dict:
#     """
#     특정 카테고리에서 싫어요(dislikes)가 많은 상위 N개의 뉴스페이퍼를 반환합니다.
#     각 뉴스페이퍼별로 싫어요 개수만 포함합니다.
#     """
#     # 카테고리 존재 여부 확인
#     category = session.exec(select(Category).where(Category.id == category_id)).first()
#     if not category:
#         raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")

#     # 1. NewspaperCategory에서 해당 category_id를 가진 모든 newspaper_id 조회 (중복 제거)
#     newspaper_ids = session.exec(
#         select(NewspaperCategory.newspaper_id)
#         .where(NewspaperCategory.category_id == category_id)
#         .distinct()
#     ).all()
    
#     if type:
#         # type 필터링이 있는 경우, 해당 type의 newspaper_id만 필터링
#         newspaper_ids = session.exec(
#             select(NewspaperCategory.newspaper_id)
#             .join(Newspaper, NewspaperCategory.newspaper_id == Newspaper.id)
#             .where(
#                 NewspaperCategory.category_id == category_id,
#                 Newspaper.type == type
#             )
#             .distinct()
#         ).all()
    
#     # 2. 각 newspaper_id에 대해 싫어요 수 계산
#     newspaper_stats = session.exec(
#         select(
#             Newspaper,
#             func.count(UserNewspaperPreference.user_id).label('dislike_count')
#         )
#         .outerjoin(UserNewspaperPreference, Newspaper.id == UserNewspaperPreference.newspaper_id)
#         .where(
#             Newspaper.id.in_(newspaper_ids),
#             UserNewspaperPreference.preference == PreferenceEnum.DISLIKE
#         )
#         .group_by(Newspaper.id)
#         .order_by(func.count(UserNewspaperPreference.user_id).desc())
#         .limit(limit)
#     ).all()
    
#     return {
#         "newspapers": [
#             {
#                 "newspaper": n.Newspaper,
#                 "dislike_count": n.dislike_count or 0
#             }
#             for n in newspaper_stats
#         ]
#     }
