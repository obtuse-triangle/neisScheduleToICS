import pytest
import re
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

    # 모든 줄바꿈이 CRLF(\r\n)인지 확인
    assert "\r\n" in ics_string
    assert "\n" not in ics_string.replace("\r\n", "")

    # 필수 ICS 구성 요소 확인
    lines = ics_string.split("\r\n")
    assert "BEGIN:VCALENDAR" in lines
    assert "END:VCALENDAR" in lines
    assert "PRODID:-//obtuse.kr//SchoolScheduleToICS//KO" in lines
    assert f"X-WR-CALNAME:{school_name} 학사일정" in lines

    # 이벤트 존재 여부 확인
    assert ics_string.count("BEGIN:VEVENT") == 2
    assert ics_string.count("END:VEVENT") == 2

    # 각 이벤트에 UID가 포함되었는지 정규식으로 확인
    assert len(re.findall(r"UID:[0-9a-fA-F\-]+", ics_string)) == 2

    # 이벤트 상세 정보 확인
    assert "SUMMARY:개교기념일" in lines
    assert "DTSTART;VALUE=DATE:20240901" in lines
    assert "DESCRIPTION:학교 쉬는 날" in lines


def test_convert_to_ics_no_events(sample_empty_data):
    """이벤트가 없는 데이터도 유효한 ICS 형식으로 변환되는지 테스트합니다."""
    school_name = "이벤트없는학교"
    ics_string = convert_to_ics(sample_empty_data, school_name)

    # 줄바꿈 및 기본 구조 확인
    assert "\r\n" in ics_string
    lines = ics_string.split("\r\n")
    assert "BEGIN:VCALENDAR" in lines
    assert "END:VCALENDAR" in lines

    # 이벤트가 없어야 함
    assert "BEGIN:VEVENT" not in lines
    assert "UID:" not in ics_string

def test_convert_to_ics_malformed_data():
    """'SchoolSchedule' 키가 없거나 형식이 다른 데이터를 처리하는지 테스트합니다."""
    malformed_data = {"Error": "Some error"}
    school_name = "오류난학교"
    ics_string = convert_to_ics(malformed_data, school_name)

    # 줄바꿈 및 기본 구조 확인
    assert "\r\n" in ics_string
    lines = ics_string.split("\r\n")
    assert "BEGIN:VCALENDAR" in lines
    assert "END:VCALENDAR" in lines

    # 이벤트는 없어야 함
    assert "BEGIN:VEVENT" not in lines
