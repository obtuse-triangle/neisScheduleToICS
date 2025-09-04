import uuid
from datetime import datetime, timezone, timedelta
from app.utils.date_utils import parse_date
from icalendar import Calendar, Event, Alarm

# UID 생성을 위한 네임스페이스 정의
ICS_NAMESPACE = uuid.NAMESPACE_DNS

def convert_to_ics(data: dict, school_name: str) -> str:
    """
    NEIS API 응답 데이터를 icalendar 라이브러리를 사용하여 ICS 형식으로 변환합니다.
    RFC 5545 표준을 완벽하게 준수합니다.
    """
    cal = Calendar()
    cal.add('prodid', '-//obtuse.kr//SchoolScheduleToICS//KO')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('X-WR-CALNAME', f"{school_name} 학사일정")
    cal.add('X-WR-TIMEZONE', 'Asia/Seoul')

    if 'SchoolSchedule' in data:
        for item in data.get('SchoolSchedule', []):
            if 'row' in item:
                for event_data in item.get('row', []):
                    event = Event()

                    event_name = event_data.get('EVENT_NM', '이름 없는 이벤트')
                    start_date = parse_date(event_data['AA_YMD'])

                    # 결정적 UID 생성
                    uid_name = f"{school_name}-{event_data['AA_YMD']}-{event_name}"
                    uid = uuid.uuid5(ICS_NAMESPACE, uid_name)

                    event.add('uid', uid)
                    event.add('summary', event_name)
                    event.add('description', event_data.get('EVENT_CNTNT', ''))
                    event.add('location', event_data.get('SCHUL_NM', ''))

                    # 종일 이벤트 설정
                    event.add('dtstart', start_date.date())

                    # DTSTAMP (생성 시각) 추가
                    event.add('dtstamp', datetime.now(timezone.utc))

                    # 투명하게 설정 (다른 일정을 가리지 않음)
                    event.add('transp', 'TRANSPARENT')

                    # 알람 추가 (하루 전)
                    alarm = Alarm()
                    alarm.add('action', 'DISPLAY')
                    alarm.add('description', event_name)
                    alarm.add('trigger', timedelta(days=-1))
                    event.add_component(alarm)

                    cal.add_component(event)

    # 라이브러리가 모든 이스케이프, 폴딩, 줄바꿈 처리를 하여 바이트 문자열로 반환
    # 이를 다시 utf-8 문자열로 디코딩하여 반환
    return cal.to_ical().decode('utf-8')
