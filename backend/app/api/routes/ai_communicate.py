from fastapi import APIRouter, HTTPException, Request
import httpx
import os

router = APIRouter(tags=["ai_server"], prefix="/ai")

ai_backend_host = os.getenv("AI_BACKEND_HOST")

@router.get("/health-check")
async def ai_health_check():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ai_backend_host}/api/utils/health-check")
            response.raise_for_status()
            return {"status": "AI 서버가 정상적으로 작동 중입니다.", "details": response.json()}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"AI 서버 오류: {exc.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
@router.get("/provide_db")
async def provide_db():
    '''
    내 db정보를 ai서버가 알 수 있게끔
    '''
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ai_backend_host}/api/database/get-dashboard")
            response.raise_for_status()
            return {"status": "데이터베이스 전달 성공.", "details": response.json()}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"데이터베이스 서버 오류: {exc.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/receive_newspapers")
async def receive_newspapers():
    '''
    AI 서버에서 정리된 파일을 내 데이터베이스로 가져오는 기능
    '''
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{ai_backend_host}/api/database/send-newspapers")
            response.raise_for_status()
            return {"status": "파일 수신 성공.", "details": response.json()}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"파일 수신 오류: {exc.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run_summarize_paper")
async def run_summarize_paper():
    '''
    AI 서버에서 논문 요약을 실행하는 기능
    '''
    try:
        async with httpx.AsyncClient(timeout=900) as client:
            response = await client.post(f"{ai_backend_host}/api/makedata/run-summarize-paper")
            response.raise_for_status()
            return {"status": "논문 요약 실행 성공.", "details": response.json()}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"논문 요약 실행 오류: {exc.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run_summarize_news")
async def run_summarize_news():
    '''
    AI 서버에서 뉴스 요약을 실행하는 기능
    '''
    try:
        async with httpx.AsyncClient(timeout=900) as client:
            response = await client.post(f"{ai_backend_host}/api/makedata/run-summarize-news")
            response.raise_for_status()
            return {"status": "뉴스 요약 실행 성공.", "details": response.json()}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"뉴스 요약 실행 오류: {exc.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


