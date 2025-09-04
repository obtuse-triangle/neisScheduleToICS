import pytest
from app.services.ics_converter import convert_to_ics

# 테스트에 사용할 샘플 데이터 정의
@pytest.fixture
def sample_schedule_data():
    """NEIS API로부터 받은 학사일정 데이터의 모의(mock) 버전."""
    return {
        "SchoolSchedule": [
            {"head": [...]}, # 실제 데이터와 유사하게 head 부분 포함
            {
                "row": [
                    {
                        "SCHUL_NM": "테스트고등학교",
                        "AA_YMD": "20240901",
                        "EVENT_NM": "개교기념일",
                        "EVENT_CNTNT": "학교 쉬는 날"
                    },
                    {
                        "SCHUL_NM": "테스트고등학교",
                        "AA_YMD": "20241009",
                        "EVENT_NM": "한글날",
                        "EVENT_CNTNT": "공휴일"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def sample_empty_data():
    """학사일정 이벤트가 없는 경우의 모의 데이터."""
    return {
        "SchoolSchedule": [
            {"head": [...]},
            {
                "row": [] # 이벤트 목록이 비어있음
            }
        ]
    }

def test_convert_to_ics_success(sample_schedule_data):
    """학사일정 데이터가 성공적으로 ICS 형식으로 변환되는지 테스트합니다."""
    school_name = "테스트고등학교"
    ics_string = convert_to_ics(sample_schedule_data, school_name)

    # 필수 ICS 구성 요소 확인
    assert "BEGIN:VCALENDAR" in ics_string
    assert "END:VCALENDAR" in ics_string
    assert "PRODID:-//obtuse.kr//SchoolScheduleToICS//KO" in ics_string
    assert f"X-WR-CALNAME:{school_name} 학사일정" in ics_string

    # 이벤트 존재 여부 확인
    assert ics_string.count("BEGIN:VEVENT") == 2
    assert ics_string.count("END:VEVENT") == 2

    # 첫 번째 이벤트의 상세 정보 확인
    assert "SUMMARY:개교기념일" in ics_string
    assert "DTSTART;VALUE=DATE:20240901" in ics_string
    assert "DESCRIPTION:학교 쉬는 날" in ics_string

    # 두 번째 이벤트의 상세 정보 확인
    assert "SUMMARY:한글날" in ics_string
    assert "DTSTART;VALUE=DATE:20241009" in ics_string
    assert "DESCRIPTION:공휴일" in ics_string


def test_convert_to_ics_no_events(sample_empty_data):
    """이벤트가 없는 데이터도 유효한 ICS 형식으로 변환되는지 테스트합니다."""
    school_name = "이벤트없는학교"
    ics_string = convert_to_ics(sample_empty_data, school_name)

    # 필수 ICS 구성 요소 확인
    assert "BEGIN:VCALENDAR" in ics_string
    assert "END:VCALENDAR" in ics_string
    assert f"X-WR-CALNAME:{school_name} 학사일정" in ics_string

    # 이벤트가 없어야 함
    assert "BEGIN:VEVENT" not in ics_string
    assert "SUMMARY:" not in ics_string

def test_convert_to_ics_malformed_data():
    """'SchoolSchedule' 키가 없거나 형식이 다른 데이터를 처리하는지 테스트합니다."""
    malformed_data = {"Error": "Some error"}
    school_name = "오류난학교"
    ics_string = convert_to_ics(malformed_data, school_name)

    # 필수 ICS 구성 요소는 여전히 존재해야 함
    assert "BEGIN:VCALENDAR" in ics_string
    assert "END:VCALENDAR" in ics_string

    # 이벤트는 없어야 함
    assert "BEGIN:VEVENT" not in ics_string
