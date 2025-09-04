"""API routes for the application."""
from fastapi import Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from models import SchoolSearch
from services import neis_service, ics_service, school_service, cache_service


templates = Jinja2Templates(directory="templates")


async def get_school(ATPT_OFCDC_SC_CODE: str, SD_SCHUL_CODE: int):
    """Get school schedule as ICS file."""
    if ATPT_OFCDC_SC_CODE is None or SD_SCHUL_CODE is None:
        return {"message": "시도교육청 코드와 학교 코드를 입력해주세요. 예) /school?ATPT_OFCDC_SC_CODE=C10&SD_SCHUL_CODE=7150658"}

    # Check cache first
    cached_content = cache_service.get_cached_content(ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE)
    if cached_content:
        file_path = cache_service.get_cache_path(ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE)
        return FileResponse(file_path, media_type='text/calendar', filename='school_schedule.ics')

    # Fetch from NEIS API and convert to ICS
    json_data = await neis_service.get_school_schedule(ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE)
    ics_data = ics_service.convert_to_ics(json_data)
    
    # Save to cache
    file_path = cache_service.save_to_cache(ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE, ics_data)
    
    return FileResponse(file_path, media_type='text/calendar', filename='school_schedule.ics')


async def index(request: Request):
    """Render the index page."""
    return templates.TemplateResponse("index.html", {"request": request})


async def school_search(school_search: SchoolSearch):
    """Search for schools."""
    result = school_service.search_schools(
        school_search.ATPT_OFCDC_SC_CODE, 
        school_search.SCHUL_NM
    )
    return JSONResponse(content=result)