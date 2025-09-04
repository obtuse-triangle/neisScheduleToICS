import requests
from fastapi import HTTPException
from datetime import datetime
from app.core.config import settings

async def get_school_schedule(ATPT_OFCDC_SC_CODE: str, SD_SCHUL_CODE: int) -> dict:
    """
    NEIS API를 호출하여 학교 학사일정 정보를 가져옵니다.
    API 키가 설정되지 않았거나, 응답에 실패하면 HTTPException을 발생시킵니다.
    """
    api_key = settings.get("neisKey")
    if not api_key or api_key == "YOUR_API_KEY" or api_key == "YOUR_API_KEY_HERE":
        # 설정 파일이 없거나, API 키가 기본값일 경우 에러 발생
        raise HTTPException(
            status_code=500,
            detail="NEIS API key is not configured in config.json."
        )

    # 올해 1월 1일부터 내년 1월 1일까지의 학사일정을 조회합니다.
    current_year = datetime.now().year
    start_date = f"{current_year}0101"
    end_date = f"{current_year + 1}0101"

    url = (
        f"https://open.neis.go.kr/hub/SchoolSchedule"
        f"?KEY={api_key}"
        f"&Type=json"
        f"&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
        f"&SD_SCHUL_CODE={SD_SCHUL_CODE}"
        f"&MLSV_FROM_YMD={start_date}"
        f"&MLSV_TO_YMD={end_date}"
        f"&pSize=1000"
    )

    print(f"Requesting NEIS API URL: {url}")

    try:
        response = requests.get(url, timeout=5) # 5초 타임아웃 설정
        response.raise_for_status()  # 4xx, 5xx 에러 발생 시 예외 발생
        return response.json()
    except requests.exceptions.HTTPError as e:
        # API 서버에서 반환한 에러 (e.g., 400, 401, 500)
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error from NEIS server: {e}"
        )
    except requests.exceptions.RequestException as e:
        # 네트워크 연결 문제, 타임아웃 등
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to NEIS server: {e}"
        )
