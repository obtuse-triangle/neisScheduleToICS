from fastapi import APIRouter
from app.controllers import school_controller
from app.models.school import SchoolSearch

router = APIRouter(
    tags=["School"],
)

@router.post("/search")
async def search_school_route(school_search: SchoolSearch):
    """
    학교를 검색합니다. `school_controller.search_school`를 호출합니다.
    """
    return await school_controller.search_school(school_search)
