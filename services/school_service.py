"""School data service for managing school information."""
import pandas as pd
from typing import List, Dict, Any


class SchoolService:
    """Service for managing school data."""
    
    def __init__(self, data_file: str = "data/학교기본정보2024_11_30.csv"):
        self.data_file = data_file
        self._school_data = self._load_school_data()
    
    def _load_school_data(self) -> pd.DataFrame:
        """Load school data from CSV file."""
        with open(self.data_file, "r", encoding='cp949') as f:
            return pd.read_csv(f)
    
    def search_schools(self, atpt_ofcdc_sc_code: str, school_name: str) -> List[Dict[str, Any]]:
        """Search for schools by education office code and name."""
        result = self._school_data[
            (self._school_data['시도교육청코드'] == atpt_ofcdc_sc_code) & (
                self._school_data['학교명'].str.contains(school_name, na=False) | 
                self._school_data['영문학교명'].str.contains(school_name, na=False)
            )
        ].fillna(value="").to_dict(orient='records')
        
        return result


# Global service instance
school_service = SchoolService()