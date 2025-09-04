from fastapi import HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.models.school import SchoolSearch
from app.services.neis import get_school_schedule
from app.services.ics_converter import convert_to_ics
from app.services.school_search import school_search_service
from app.services.cache_service import cache_service

async def search_school(school_search: SchoolSearch) -> JSONResponse:
    """
    학교 이름으로 검색하여 결과를 반환합니다. (이 함수는 변경되지 않음)
    """
    result = school_search_service.search(
        atpt_ofcdc_sc_code=school_search.ATPT_OFCDC_SC_CODE,
        schul_nm=school_search.SCHUL_NM
    )
    return JSONResponse(content=result)


async def get_school_calendar(atpt_ofcdc_sc_code: str, sd_schul_code: int) -> FileResponse:
    """
    지정된 학교의 학사일정을 ICS 파일로 반환합니다.
    캐시 서비스를 사용하여 결과를 캐시합니다.
    """
    if not atpt_ofcdc_sc_code or not sd_schul_code:
        raise HTTPException(
            status_code=400,
            detail="ATPT_OFCDC_SC_CODE and SD_SCHUL_CODE are required."
        )

    # 1. 캐시 확인
    cached_path = cache_service.get(atpt_ofcdc_sc_code, sd_schul_code)
    if cached_path:
        return FileResponse(cached_path, media_type='text/calendar', filename='school_schedule.ics')

    # 2. 캐시 미스: 데이터 생성
    print(f"Cache miss for {atpt_ofcdc_sc_code}/{sd_schul_code}. Fetching from NEIS API.")

    # 학교 정보 조회 (학교 이름을 ICS 파일에 사용하기 위함)
    school_info_list = school_search_service.search(atpt_ofcdc_sc_code, "")
    target_school = next((s for s in school_info_list if s.get('행정표준코드') == str(sd_schul_code)), None)

    if not target_school:
        raise HTTPException(status_code=404, detail=f"School with code {sd_schul_code} not found in local data for region {atpt_ofcdc_sc_code}.")

    school_name = target_school.get('학교명', 'Unknown School')

    # NEIS API에서 학사일정 데이터 가져오기
    json_data = await get_school_schedule(atpt_ofcdc_sc_code, sd_schul_code)

    # NEIS API가 데이터 없음을 반환하는 경우 처리 ("INFO-200"은 데이터 없음을 의미)
    if "RESULT" in json_data and json_data["RESULT"]["CODE"] == "INFO-200":
        raise HTTPException(status_code=404, detail="No schedule data found for the given school on NEIS.")

    # ICS 형식으로 변환
    ics_data = convert_to_ics(json_data, school_name)

    # 3. 생성된 데이터를 캐시에 저장
    newly_cached_path = cache_service.set(atpt_ofcdc_sc_code, sd_schul_code, ics_data)

    # 4. 새로 캐시된 파일 반환
    return FileResponse(newly_cached_path, media_type='text/calendar', filename='school_schedule.ics')
