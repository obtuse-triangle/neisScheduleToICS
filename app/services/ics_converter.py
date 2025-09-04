import uuid
from datetime import datetime, timezone
from app.utils.date_utils import parse_date, format_date

# UDI 생성을 위한 네임스페이스 정의
ICS_NAMESPACE = uuid.NAMESPACE_DNS

def convert_to_ics(data: dict, school_name: str) -> str:
    """
    NEIS API 응답 데이터를 ICS 형식의 문자열로 변환합니다.
    RFC 5545 호환성을 위해 UID와 CRLF 줄바꿈을 포함합니다.
    """
    now_utc = datetime.now(timezone.utc)
    today = now_utc.strftime('%Y%m%dT%H%M%SZ')

    # 리스트에 각 라인을 추가한 후 join하여 성능을 개선하고 가독성을 높입니다.
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//obtuse.kr//SchoolScheduleToICS//KO",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{school_name} 학사일정",
        "X-WR-TIMEZONE:Asia/Seoul",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Seoul",
        "TZURL:https://www.tzurl.org/zoneinfo-outlook/Asia/Seoul",
        "X-LIC-LOCATION:Asia/Seoul",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZNAME:KST",
        "TZOFFSETFROM:+0900",
        "TZOFFSETTO:+0900",
        "END:STANDARD",
        "END:VTIMEZONE",
        f"X-CREATED-TIME:{now_utc.isoformat().replace('+00:00', 'Z')}"
    ]

    if 'SchoolSchedule' in data:
        for item in data.get('SchoolSchedule', []):
            if 'row' in item:
                for event in item.get('row', []):
                    start_date = parse_date(event['AA_YMD'])

                    # 예측 가능한 고유 ID 생성
                    uid_name = f"{school_name}-{event['AA_YMD']}-{event['EVENT_NM']}"
                    uid = uuid.uuid5(ICS_NAMESPACE, uid_name)

                    ics_lines.extend([
                        "BEGIN:VEVENT",
                        f"UID:{uid}",
                        f"DTSTART;VALUE=DATE:{format_date(start_date)}",
                        "TRANSP:OPAQUE",
                        f"DTSTAMP:{today}",
                        "X-MICROSOFT-CDO-BUSYSTATUS:BUSY",
                        "CLASS:PUBLIC",
                        "BEGIN:VALARM",
                        f"DESCRIPTION:{event['EVENT_NM']}",
                        "TRIGGER:-P1D",
                        "END:VALARM",
                        f"SUMMARY:{event['EVENT_NM']}",
                        f"DESCRIPTION:{event['EVENT_CNTNT']}",
                        f"LOCATION:{event['SCHUL_NM']}",
                        "END:VEVENT"
                    ])

    ics_lines.append("END:VCALENDAR")

    # 모든 라인을 CRLF(\r\n)로 조합하여 최종 ICS 문자열 생성
    return "\r\n".join(ics_lines)
