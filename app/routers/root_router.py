from fastapi import APIRouter, Request
from app.controllers import root_controller

router = APIRouter()

@router.get("/")
async def get_root(request: Request):
    """
    루트 경로 ('/')에 대한 GET 요청을 처리합니다.
    root_controller에 정의된 로직을 호출합니다.
    """
    return await root_controller.get_index_page(request)
