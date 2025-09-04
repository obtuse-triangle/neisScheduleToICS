from fastapi import APIRouter
from app.controllers import school_controller

router = APIRouter(
    prefix="/school",
    tags=["School"],
)

@router.get("")
async def get_school_calendar_route(ATPT_OFCDC_SC_CODE: str, SD_SCHUL_CODE: int):
    """
    학교 코드를 사용하여 학사일정 ICS 파일을 가져옵니다.
    `school_controller.get_school_calendar`를 호출합니다.

    (참고: prefix가 /school이므로 이 엔드포인트의 전체 경로는 /school이 됩니다.)
    """
    return await school_controller.get_school_calendar(ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE)
