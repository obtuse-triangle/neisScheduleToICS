from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# 라우터 모듈들을 가져옵니다.
from app.routers import root_router, school_router, search_router

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="나이스 학사일정 ICS 변환기",
    description="나이스(NEIS) 학사일정 정보를 조회하여 iCalendar(.ics) 파일로 변환하는 API 서버입니다.",
    version="2.0.0",
)

# 정적 파일 마운트 ("static" 폴더)
# 이 설정은 템플릿(index.html)이 /static/script.js를 참조할 수 있도록 합니다.
app.mount("/static", StaticFiles(directory="static"), name="static")

# 분리된 라우터들을 앱에 포함시킵니다.
# 이렇게 하면 각 라우터 파일에 정의된 경로들이 앱에 등록됩니다.
app.include_router(root_router.router)
app.include_router(school_router.router)
app.include_router(search_router.router)

# 참고: 이제 이 파일에는 더 이상 @app.get, @app.post와 같은
# 개별 엔드포인트 데코레이터가 존재하지 않습니다.
# 모든 라우팅 로직은 app/routers/ 디렉토리에서 관리됩니다.
