"""NEIS API service for fetching school schedule data."""
import requests
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException

from config import settings


class NeisService:
    """Service for interacting with NEIS API."""
    
    def __init__(self):
        self.base_url = "https://open.neis.go.kr/hub/SchoolSchedule"
    
    async def get_school_schedule(self, atpt_ofcdc_sc_code: str, sd_schul_code: int) -> Dict[str, Any]:
        """Fetch school schedule from NEIS API."""
        url = f"{self.base_url}?KEY={settings.neis_key}&Type=json&ATPT_OFCDC_SC_CODE={atpt_ofcdc_sc_code}&SD_SCHUL_CODE={sd_schul_code}&MLSV_FROM_YMD={datetime.now().year}0101&MLSV_TO_YMD={(datetime.now().year + 1)}0101&pSize=1000"
        
        print(url)  # For debugging
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error fetching data from NEIS server"
            )


# Global service instance
neis_service = NeisService()