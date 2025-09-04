import pytest
import requests
from fastapi import HTTPException

from app.services import neis
from app.core.config import settings

# 비동기 테스트를 위해 pytest.mark.asyncio 사용
pytestmark = pytest.mark.asyncio

NEIS_API_URL = "https://open.neis.go.kr/hub/SchoolSchedule"

@pytest.fixture
def mock_settings(mocker):
    """테스트를 위한 유효한 API 키를 가진 설정 모의 객체."""
    mocker.patch.dict(settings, {"neisKey": "TEST_API_KEY"})
    return settings

async def test_get_school_schedule_success(mock_settings, mocker):
    """NEIS API 호출이 성공하고, 유효한 JSON 데이터를 반환하는 경우를 테스트합니다."""
    # --- 준비 (Arrange) ---
    mock_response_data = {"SchoolSchedule": [{"row": [{"EVENT_NM": "방학"}]}]}
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch('requests.get', return_value=mock_response)

    # --- 실행 (Act) ---
    result = await neis.get_school_schedule("C10", 7150658)

    # --- 단언 (Assert) ---
    requests.get.assert_called_once()
    assert result == mock_response_data

async def test_get_school_schedule_api_error_in_json(mock_settings, mocker):
    """NEIS API가 200 OK와 함께 에러 메시지를 반환하는 경우를 테스트합니다."""
    # --- 준비 (Arrange) ---
    error_response_data = {"RESULT": {"CODE": "ERROR-290", "MESSAGE": "인증키가 유효하지 않습니다."}}
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = error_response_data
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch('requests.get', return_value=mock_response)

    # --- 실행 및 단언 (Act & Assert) ---
    with pytest.raises(HTTPException) as exc_info:
        await neis.get_school_schedule("C10", 7150658)

    assert exc_info.value.status_code == 400
    assert "인증키가 유효하지 않습니다." in exc_info.value.detail

async def test_get_school_schedule_http_error(mock_settings, mocker):
    """NEIS API가 500 서버 에러를 반환할 때 HTTPException이 발생하는지 테스트합니다."""
    # --- 준비 (Arrange) ---
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mocker.Mock(status_code=500))
    mocker.patch('requests.get', return_value=mock_response)

    # --- 실행 및 단언 (Act & Assert) ---
    with pytest.raises(HTTPException) as exc_info:
        await neis.get_school_schedule("C10", 7150658)

    assert exc_info.value.status_code == 500
    assert "HTTP Error from NEIS server" in exc_info.value.detail

async def test_get_school_schedule_connection_timeout(mock_settings, mocker):
    """API 서버 연결 시간 초과 시 HTTPException이 발생하는지 테스트합니다."""
    # --- 준비 (Arrange) ---
    mocker.patch('requests.get', side_effect=requests.exceptions.ConnectTimeout)

    # --- 실행 및 단언 (Act & Assert) ---
    with pytest.raises(HTTPException) as exc_info:
        await neis.get_school_schedule("C10", 7150658)

    assert exc_info.value.status_code == 503
    assert "Could not connect to NEIS server" in exc_info.value.detail

async def test_get_school_schedule_no_api_key(mocker):
    """API 키가 설정되지 않았을 때 HTTPException이 발생하는지 테스트합니다."""
    # API 키를 빈 값으로 설정
    mocker.patch.dict(settings, {"neisKey": ""})

    with pytest.raises(HTTPException) as exc_info:
        await neis.get_school_schedule("C10", 7150658)

    assert exc_info.value.status_code == 500
    assert "NEIS API key is not configured" in exc_info.value.detail
