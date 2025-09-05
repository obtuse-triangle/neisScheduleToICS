import pytest
from fastapi.testclient import TestClient
from pathlib import Path

# 테스트 대상 FastAPI 앱 임포트
from app.main import app

# 서비스 모킹을 위해 각 서비스 인스턴스를 임포트
from app.services import school_search, cache_service, neis, ics_converter

@pytest.fixture
def client():
    """테스트용 TestClient 인스턴스를 생성하는 픽스처."""
    with TestClient(app) as c:
        yield c

def test_get_root(client):
    """메인 페이지('/')를 성공적으로 가져오는지 테스트합니다."""
    response = client.get("/")
    assert response.status_code == 200
    assert "나이스 학사일정 캘린더" in response.text
    assert response.headers['content-type'] == 'text/html; charset=utf-8'

def test_search_school_success(client, mocker):
    """학교 검색 API('/search')가 성공적으로 동작하는지 테스트합니다."""
    # --- 준비 (Arrange) ---
    mock_search_result = [{"학교명": "테스트고", "행정표준코드": "1234"}]
    # school_search_service의 search 메서드를 모킹합니다.
    mocker.patch.object(school_search.school_search_service, 'search', return_value=mock_search_result)

    # --- 실행 (Act) ---
    response = client.post("/search", json={"ATPT_OFCDC_SC_CODE": "B10", "SCHUL_NM": "테스트"})

    # --- 단언 (Assert) ---
    assert response.status_code == 200
    assert response.json() == mock_search_result

def test_get_school_calendar_cache_hit(client, mocker, tmp_path):
    """캐시된 캘린더 파일을 성공적으로 반환하는지 테스트합니다."""
    # --- 준비 (Arrange) ---
    # 임시 ICS 파일 생성
    dummy_ics_content = "BEGIN:VCALENDAR\nEND:VCALENDAR"
    dummy_file = tmp_path / "dummy.ics"
    dummy_file.write_text(dummy_ics_content)

    # cache_service.get 메서드가 임시 파일 경로를 반환하도록 모킹
    mocker.patch.object(cache_service.cache_service, 'get', return_value=dummy_file)

    # --- 실행 (Act) ---
    response = client.get("/school?ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=1234")

    # --- 단언 (Assert) ---
    assert response.status_code == 200
    assert response.text == dummy_ics_content
    assert response.headers['content-type'].startswith('text/calendar')

def test_get_school_calendar_cache_miss_and_create(client, mocker, tmp_path):
    """캐시 미스 시, 새로운 캘린더를 생성하고 반환하는지 테스트합니다."""
    # --- 준비 (Arrange) ---
    # 1. 외부 의존성 및 파일 시스템 상호작용 모킹

    # cache_service.get()은 캐시 미스를 반환해야 함
    mocker.patch.object(cache_service.cache_service, 'get', return_value=None)

    # neis.get_school_schedule는 외부 API 호출이므로 모킹
    mock_neis_data = {
        "SchoolSchedule": [{}, {"row": [{"SCHUL_NM": "서울소프트웨어마이스터고", "AA_YMD": "20241225", "EVENT_NM": "크리스마스", "EVENT_CNTNT": "공휴일"}]}]
    }
    # school_controller에서 get_school_schedule를 직접 참조하므로, 해당 위치에서 패치해야 합니다.
    mocker.patch('app.controllers.school_controller.get_school_schedule', new_callable=mocker.AsyncMock, return_value=mock_neis_data)

    # school_search_service는 실제 CSV 대신 모의 데이터를 사용하도록 모킹
    mock_school_info = [{"학교명": "서울소프트웨어마이스터고", "행정표준코드": "1234"}]
    mocker.patch.object(school_search.school_search_service, 'search', return_value=mock_school_info)

    # cache_service의 base_dir을 임시 디렉토리로 변경하여 실제 'cache' 폴더에 쓰지 않도록 함
    mocker.patch.object(cache_service.cache_service, 'base_dir', tmp_path)

    # neis.py가 사용하는 settings에 API 키가 있도록 모킹
    mocker.patch.dict(neis.settings, {"neisKey": "TEST_API_KEY"})

    # --- 실행 (Act) ---
    # 내부 로직(ics_converter, cache_service.set)은 실제 코드를 실행
    response = client.get("/school?ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=1234")

    # --- 단언 (Assert) ---
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/calendar')

    # 응답 내용이 예상대로 생성되었는지 확인
    response_text = response.text
    assert "BEGIN:VCALENDAR" in response_text
    assert "SUMMARY:크리스마스" in response_text
    assert "DTSTART;VALUE=DATE:20241225" in response_text

    # 캐시 파일이 실제로 생성되었는지 확인
    expected_cache_file = tmp_path / "B10" / "1234.ics"
    assert expected_cache_file.exists()
    assert "SUMMARY:크리스마스" in expected_cache_file.read_text(encoding='utf-8')
