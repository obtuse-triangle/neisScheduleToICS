import pytest
from datetime import datetime, timedelta, timezone
from app.services.cache_service import CacheService

# 테스트용 키와 콘텐츠
TEST_ATPT_CODE = "T10"
TEST_SCHOOL_CODE = 12345678
TEST_ICS_CONTENT_TEMPLATE = """BEGIN:VCALENDAR
X-CREATED-TIME:{}
BEGIN:VEVENT
SUMMARY:Some Event
END:VEVENT
END:VCALENDAR"""

@pytest.fixture
def cache_service(tmp_path):
    """테스트용 CacheService 인스턴스를 생성하는 픽스처."""
    # 7일짜리 캐시 서비스를 생성
    return CacheService(base_dir=str(tmp_path), duration_days=7)

def test_cache_set_and_get_hit(cache_service):
    """캐시에 데이터를 저장하고, 유효한 기간 내에 성공적으로 가져오는지 테스트합니다."""
    # 현재 시간으로 ICS 콘텐츠 생성
    now_utc = datetime.now(timezone.utc)
    # icalendar 라이브러리가 생성하는 포맷으로 변경
    timestamp_str = now_utc.strftime('%Y%m%dT%H%M%SZ')
    content = TEST_ICS_CONTENT_TEMPLATE.format(timestamp_str)

    # 1. 캐시 설정
    cache_path = cache_service.set(TEST_ATPT_CODE, TEST_SCHOOL_CODE, content)

    # 파일이 실제로 생성되었는지 확인
    assert cache_path.exists()
    assert cache_path.read_text(encoding="utf8") == content

    # 2. 캐시 가져오기 (Cache Hit)
    retrieved_path = cache_service.get(TEST_ATPT_CODE, TEST_SCHOOL_CODE)

    assert retrieved_path is not None
    assert retrieved_path == cache_path

def test_cache_get_miss(cache_service):
    """존재하지 않는 캐시 키에 대해 None을 반환하는지 테스트합니다."""
    retrieved_path = cache_service.get("NON_EXISTENT_CODE", 999999)
    assert retrieved_path is None

def test_cache_get_expired(cache_service):
    """캐시가 만료되었을 때 None을 반환하는지 테스트합니다."""
    # --- 준비 (Arrange) ---
    fake_now = datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    eight_days_ago = fake_now - timedelta(days=8)

    # 1. 8일 전의 시간으로 캐시 파일을 생성합니다.
    timestamp_str = eight_days_ago.strftime('%Y%m%dT%H%M%SZ')
    expired_content = TEST_ICS_CONTENT_TEMPLATE.format(timestamp_str)
    cache_service.set(TEST_ATPT_CODE, TEST_SCHOOL_CODE, expired_content)

    # --- 실행 (Act) ---
    # get()을 호출할 때 '현재 시간'으로 fake_now를 주입합니다.
    retrieved_path = cache_service.get(
        TEST_ATPT_CODE,
        TEST_SCHOOL_CODE,
        now_func=lambda: fake_now
    )

    # --- 단언 (Assert) ---
    assert retrieved_path is None

def test_cache_get_invalid_timestamp(cache_service):
    """타임스탬프가 없는 캐시 파일에 대해 None을 반환하는지 테스트합니다."""
    # X-CREATED-TIME이 없는 잘못된 콘텐츠
    invalid_content = "BEGIN:VCALENDAR\nEND:VCALENDAR"

    cache_path = cache_service.set(TEST_ATPT_CODE, TEST_SCHOOL_CODE, invalid_content)
    assert cache_path.exists()

    retrieved_path = cache_service.get(TEST_ATPT_CODE, TEST_SCHOOL_CODE)
    assert retrieved_path is None
