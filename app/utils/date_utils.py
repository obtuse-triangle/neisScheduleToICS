from datetime import datetime

def parse_date(date_string: str) -> datetime:
    """YYYYMMDD 형식의 문자열을 datetime 객체로 변환합니다."""
    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[6:8])
    return datetime(year, month, day)

def format_date(date: datetime) -> str:
    """datetime 객체를 YYYYMMDD 형식의 문자열로 변환합니다."""
    return date.strftime("%Y%m%d")
