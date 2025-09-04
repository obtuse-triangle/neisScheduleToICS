from datetime import datetime, timezone
from app.utils.date_utils import parse_date, format_date

def convert_to_ics(data: dict, school_name: str) -> str:
    """
    NEIS API 응답 데이터를 ICS 형식의 문자열로 변환합니다.
    """
    now_utc = datetime.now(timezone.utc)
    today = now_utc.strftime('%Y%m%dT%H%M%SZ')

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//obtuse.kr//SchoolScheduleToICS//KO
CALSCALE:GREGORIAN
X-WR-CALNAME:{school_name} 학사일정
X-WR-TIMEZONE:Asia/Seoul
BEGIN:VTIMEZONE
TZID:Asia/Seoul
TZURL:https://www.tzurl.org/zoneinfo-outlook/Asia/Seoul
X-LIC-LOCATION:Asia/Seoul
BEGIN:STANDARD
DTSTART:19700101T000000
TZNAME:KST
TZOFFSETFROM:+0900
TZOFFSETTO:+0900
END:STANDARD
END:VTIMEZONE
X-CREATED-TIME:{now_utc.isoformat().replace('+00:00', 'Z')}\n"""

    if 'SchoolSchedule' in data:
        for item in data['SchoolSchedule']:
            if 'row' in item:
                for event in item['row']:
                    start_date = parse_date(event['AA_YMD'])
                    ics += f"""BEGIN:VEVENT
DTSTART;VALUE=DATE:{format_date(start_date)}
TRANSP:OPAQUE
DTSTAMP:{today}
X-MICROSOFT-CDO-BUSYSTATUS:BUSY
CLASS:PUBLIC
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:{event['EVENT_NM']}
TRIGGER:-P1D
END:VALARM
SUMMARY:{event['EVENT_NM']}
DESCRIPTION:{event['EVENT_CNTNT']}
LOCATION:{event['SCHUL_NM']}
END:VEVENT\n"""
    ics += "END:VCALENDAR"
    return ics
