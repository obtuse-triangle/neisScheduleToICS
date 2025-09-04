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
        response = requests.get(url, timeout=10) # 타임아웃 10초로 증가
        response.raise_for_status()
        json_data = response.json()

        # NEIS API는 200 OK와 함께 에러 코드를 반환할 수 있음
        if "RESULT" in json_data:
            result_code = json_data["RESULT"]["CODE"]
            if result_code != "INFO-000":
                raise HTTPException(
                    status_code=400, # 클라이언트 요청이 잘못되었을 가능성이 높음 (e.g., 잘못된 학교 코드)
                    detail=f"NEIS API Error: {json_data['RESULT']['MESSAGE']} (Code: {result_code})"
                )

        return json_data

    except requests.exceptions.HTTPError as e:
        # 4xx, 5xx 에러
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"HTTP Error from NEIS server: {e}"
        )
    except requests.exceptions.RequestException as e:
        # 연결 시간 초과, DNS 문제 등
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to NEIS server: {e}"
        )
