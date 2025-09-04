import pytest
from app.services.ics_converter import convert_to_ics
from icalendar import Calendar

@pytest.fixture
def sample_schedule_data():
    """A mock version of the schedule data from the NEIS API."""
    return {
        "SchoolSchedule": [
            {"head": [...]},
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
                        "EVENT_NM": "한글날, 공휴일", # 쉼표가 포함된 이벤트명
                        "EVENT_CNTNT": "공식적인 공휴일입니다."
                    }
                ]
            }
        ]
    }

def test_convert_to_ics_with_icalendar_lib(sample_schedule_data):
    """
    icalendar 라이브러리를 사용한 ICS 생성이 올바르게 동작하는지 테스트합니다.
    """
    school_name = "테스트고등학교"
    ics_string = convert_to_ics(sample_schedule_data, school_name)

    # 1. 생성된 문자열이 유효한 ICS인지 파싱해본다.
    cal = Calendar.from_ical(ics_string)

    # 2. VCALENDAR 속성 확인
    assert cal['prodid'] == '-//obtuse.kr//SchoolScheduleToICS//KO'
    assert cal['X-WR-CALNAME'] == f"{school_name} 학사일정"

    # 3. 이벤트 개수 확인
    events = list(cal.walk('vevent'))
    assert len(events) == 2

    # 4. 첫 번째 이벤트 상세 정보 확인
    event1 = events[0]
    assert event1['summary'] == "개교기념일"
    assert event1['description'] == "학교 쉬는 날"
    assert event1['location'] == "테스트고등학교"
    assert event1['transp'] == "TRANSPARENT"
    assert event1['dtstart'].to_ical() == b'20240901'
    assert 'uid' in event1

    # 5. 두 번째 이벤트에서 특수 문자(쉼표)가 올바르게 이스케이프 처리 되었는지 확인
    # icalendar 라이브러리는 파싱 시 이스케이프를 자동으로 해제하므로,
    # 파싱된 객체의 값을 직접 확인하면 됩니다.
    event2 = events[1]
    assert event2['summary'] == "한글날, 공휴일"

    # 원본 문자열에서 이스케이프 처리된 것을 직접 확인할 수도 있습니다.
    assert "SUMMARY:한글날\\, 공휴일" in ics_string

def test_convert_to_ics_empty_data():
    """
    이벤트 데이터가 없을 때도 비어있는 유효한 캘린더를 생성하는지 테스트합니다.
    """
    empty_data = {"SchoolSchedule": [{"row": []}]}
    school_name = "이벤트없는학교"
    ics_string = convert_to_ics(empty_data, school_name)

    cal = Calendar.from_ical(ics_string)
    events = list(cal.walk('vevent'))
    assert len(events) == 0
    assert cal['X-WR-CALNAME'] == f"{school_name} 학사일정"
