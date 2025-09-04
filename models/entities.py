"""Data entity classes."""
from typing import Dict, List, Any
from datetime import datetime


class SchoolEvent:
    """Represents a school event from NEIS API."""
    
    def __init__(self, event_data: Dict[str, Any]):
        self.date = event_data.get('AA_YMD', '')
        self.event_name = event_data.get('EVENT_NM', '')
        self.event_content = event_data.get('EVENT_CNTNT', '')
        self.school_name = event_data.get('SCHUL_NM', '')


class SchoolSchedule:
    """Represents a complete school schedule."""
    
    def __init__(self, schedule_data: Dict[str, Any]):
        self.events: List[SchoolEvent] = []
        self.school_name = ""
        
        if 'SchoolSchedule' in schedule_data:
            for item in schedule_data['SchoolSchedule']:
                if 'row' in item:
                    for event_data in item['row']:
                        event = SchoolEvent(event_data)
                        self.events.append(event)
                        if not self.school_name and event.school_name:
                            self.school_name = event.school_name