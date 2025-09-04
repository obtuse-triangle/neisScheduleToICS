"""ICS conversion service for converting school data to ICS format."""
from datetime import datetime
from typing import Dict, Any

from utils import parse_date, format_date
from models import SchoolSchedule, SchoolEvent


class IcsService:
    """Service for converting school schedules to ICS format."""
    
    def convert_to_ics(self, data: Dict[str, Any]) -> str:
        """Convert NEIS schedule data to ICS format."""
        schedule = SchoolSchedule(data)
        today = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//obtuse.kr//SchoolScheduleToICS//KO
CALSCALE:GREGORIAN
X-WR-CALNAME:{schedule.school_name} 학사일정
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
X-CREATED-TIME:{datetime.utcnow().isoformat()}\n"""

        for event in schedule.events:
            start_date = parse_date(event.date)
            ics += f"""BEGIN:VEVENT
DTSTART;VALUE=DATE:{format_date(start_date)}
TRANSP:OPAQUE
DTSTAMP:{today}
X-MICROSOFT-CDO-BUSYSTATUS:BUSY
CLASS:PUBLIC
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:{event.event_name}
TRIGGER:-P1D
END:VALARM
SUMMARY:{event.event_name}
DESCRIPTION:{event.event_content}
LOCATION:{event.school_name}
END:VEVENT\n"""
        
        ics += "END:VCALENDAR"
        return ics


# Global service instance
ics_service = IcsService()