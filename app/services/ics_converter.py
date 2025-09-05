import uuid
from datetime import datetime, timezone, timedelta
from app.utils.date_utils import parse_date
from icalendar import Calendar, Event, Alarm

# UID 생성을 위한 네임스페이스 정의
ICS_NAMESPACE = uuid.NAMESPACE_DNS

def _group_consecutive_events(event_rows: list) -> list:
    """
    이름이 같고 날짜가 연속되는 이벤트들을 그룹화합니다.
    """
    if not event_rows:
        return []

    # 날짜순으로 정렬
    try:
        sorted_events = sorted(event_rows, key=lambda x: x['AA_YMD'])
    except KeyError:
        # 'AA_YMD' 키가 없는 경우 처리
        return []

    grouped_events = []
    current_group = None

    for event in sorted_events:
        event_name = event.get('EVENT_NM')
        try:
            event_date = parse_date(event['AA_YMD'])
        except (KeyError, ValueError):
            continue # 날짜 파싱 불가 시 해당 이벤트 건너뛰기

        if current_group is None:
            # 첫 번째 그룹 시작
            current_group = {
                'name': event_name,
                'start_date': event_date,
                'end_date': event_date,
                'description': event.get('EVENT_CNTNT', ''),
                'location': event.get('SCHUL_NM', '')
            }
        elif event_name == current_group['name'] and event_date == current_group['end_date'] + timedelta(days=1):
            # 그룹 확장
            current_group['end_date'] = event_date
        else:
            # 현재 그룹을 저장하고 새 그룹 시작
            grouped_events.append(current_group)
            current_group = {
                'name': event_name,
                'start_date': event_date,
                'end_date': event_date,
                'description': event.get('EVENT_CNTNT', ''),
                'location': event.get('SCHUL_NM', '')
            }

    # 마지막 그룹 추가
    if current_group:
        grouped_events.append(current_group)

    return grouped_events

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
    # 캐시 확인을 위한 커스텀 생성 시간 속성 추가
    cal.add('X-CREATED-TIME', datetime.now(timezone.utc))

    if 'SchoolSchedule' in data:
        all_event_rows = []
        for item in data.get('SchoolSchedule', []):
            if 'row' in item:
                all_event_rows.extend(item.get('row', []))

        # "토요휴업일" 이벤트 필터링
        filtered_events = [
            event for event in all_event_rows
            if event.get('EVENT_NM') != '토요휴업일'
        ]

        merged_events = _group_consecutive_events(filtered_events)

        for merged_event in merged_events:
            event = Event()

            event_name = merged_event['name']
            start_date = merged_event['start_date']
            end_date = merged_event['end_date']

            # UID는 이벤트 이름과 시작 날짜를 기반으로 생성하여 일관성 유지
            uid_name = f"{school_name}-{start_date.strftime('%Y%m%d')}-{event_name}"
            uid = uuid.uuid5(ICS_NAMESPACE, uid_name)

            event.add('uid', uid)
            event.add('summary', event_name)
            event.add('description', merged_event['description'])
            event.add('location', merged_event['location'])

            # 종일 이벤트 설정
            event.add('dtstart', start_date.date())
            if start_date != end_date:
                # 여러 날 이벤트의 경우 DTEND는 마지막 날의 다음 날로 설정
                event.add('dtend', end_date.date() + timedelta(days=1))

            event.add('dtstamp', datetime.now(timezone.utc))
            event.add('transp', 'TRANSPARENT')

            # 알람 추가 (시작일 하루 전)
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', event_name)
            alarm.add('trigger', timedelta(days=-1, hours=-15)) # 시작일 9시 (KST 기준)
            event.add_component(alarm)

            cal.add_component(event)

    # 라이브러리가 모든 이스케이프, 폴딩, 줄바꿈 처리를 하여 바이트 문자열로 반환
    # 이를 다시 utf-8 문자열로 디코딩하여 반환
    return cal.to_ical().decode('utf-8')
