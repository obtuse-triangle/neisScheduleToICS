"""Cache service for managing cached ICS files."""
import os
import re
from datetime import datetime, timedelta
from typing import Optional

from config import settings
from utils import ensure_directory_existence


class CacheService:
    """Service for managing cached ICS files."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
    
    def get_cache_path(self, atpt_ofcdc_sc_code: str, sd_schul_code: int) -> str:
        """Get the cache file path for given school codes."""
        return os.path.join(self.cache_dir, atpt_ofcdc_sc_code, f"{sd_schul_code}.ics")
    
    def get_cached_content(self, atpt_ofcdc_sc_code: str, sd_schul_code: int) -> Optional[str]:
        """Get cached ICS content if valid, otherwise return None."""
        file_path = self.get_cache_path(atpt_ofcdc_sc_code, sd_schul_code)
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, "r", encoding="utf8") as file:
            content = file.read()
            match = re.search(
                r'X-CREATED-TIME:(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}.\d{3}Z', 
                content
            )
            
            if match and datetime.now() - datetime.fromisoformat(match.group(1)) < timedelta(days=settings.cache_days):
                return content
        
        return None
    
    def save_to_cache(self, atpt_ofcdc_sc_code: str, sd_schul_code: int, content: str) -> str:
        """Save ICS content to cache and return the file path."""
        file_path = self.get_cache_path(atpt_ofcdc_sc_code, sd_schul_code)
        ensure_directory_existence(file_path)
        
        with open(file_path, "w", encoding="utf8") as file:
            file.write(content)
        
        return file_path


# Global service instance
cache_service = CacheService()