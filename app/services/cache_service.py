import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.utils.file_utils import ensure_directory_existence

class CacheService:
    """
    파일 기반 캐시를 관리하는 서비스 클래스입니다.
    ICS 파일을 지정된 기간 동안 저장하고 재사용합니다.
    """
    def __init__(self, base_dir: str, duration_days: int):
        self.base_dir = Path(base_dir)
        self.duration = timedelta(days=duration_days)

    def _get_file_path(self, atpt_code: str, school_code: int) -> Path:
        """캐시 키에 해당하는 파일 경로를 생성합니다."""
        return self.base_dir / atpt_code / f"{school_code}.ics"

    def get(self, atpt_code: str, school_code: int, now_func=lambda: datetime.now(timezone.utc)) -> Optional[Path]:
        """
        유효한 캐시 항목을 확인하고, 존재할 경우 파일 경로를 반환합니다.
        캐시가 없거나 만료된 경우 None을 반환합니다.
        테스트를 위해 현재 시간을 주입할 수 있도록 now_func 파라미터를 추가합니다.
        """
        file_path = self._get_file_path(atpt_code, school_code)

        if not file_path.exists():
            return None

        try:
            content = file_path.read_text(encoding="utf8")
            # icalendar 라이브러리가 생성하는 실제 포맷(YYYY-MM-DD HH:MM:SS.ffffff+zz:zz)을 파싱합니다.
            match = re.search(r'X-CREATED-TIME:(.+)', content)

            if not match:
                return None

            created_time_str = match.group(1).strip()
            # fromisoformat는 이 포맷을 직접 처리할 수 있습니다.
            created_time_aware = datetime.fromisoformat(created_time_str)

            # UTC 기준으로 비교하기 위해 모든 시간을 aware datetime으로 통일합니다.
            now_aware = now_func()
            if now_aware - created_time_aware < self.duration:
                print(f"Cache hit for {atpt_code}/{school_code}.")
                return file_path
            else:
                print(f"Cache expired for {atpt_code}/{school_code}.")
                return None

        except (ValueError, IndexError, FileNotFoundError) as e:
            # 파일 읽기 또는 파싱 중 오류 발생 시 캐시 미스로 처리합니다.
            print(f"Error reading cache file '{file_path}', treating as miss: {e}")
            return None

    def set(self, atpt_code: str, school_code: int, content: str) -> Path:
        """
        주어진 콘텐츠를 캐시 파일에 저장합니다.
        """
        file_path = self._get_file_path(atpt_code, school_code)
        # 파일 경로의 디렉토리가 존재하는지 확인하고 없으면 생성합니다.
        ensure_directory_existence(str(file_path))

        file_path.write_text(content, encoding="utf8")
        print(f"Cache created/updated for {atpt_code}/{school_code}.")
        return file_path

# 애플리케이션 전역에서 사용할 단일 캐시 서비스 인스턴스를 생성합니다.
# 설정 파일에서 캐시 유지 기간을 가져와 초기화합니다.
cache_service = CacheService(
    base_dir="cache",
    duration_days=settings.get('cache_day', 7)
)
