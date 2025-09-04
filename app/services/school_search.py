import pandas as pd
from pathlib import Path

class SchoolSearchService:
    def __init__(self, data_file_path: Path):
        self.data_file_path = data_file_path
        self.school_data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """학교 정보 CSV 파일을 로드합니다."""
        try:
            # Use pathlib's open method for cleaner path handling
            with self.data_file_path.open("r", encoding='cp949') as f:
                df = pd.read_csv(f)
                print("School data loaded successfully.")
                return df
        except FileNotFoundError:
            print(f"Error: Data file not found at {self.data_file_path}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error loading school data: {e}")
            return pd.DataFrame()

    def search(self, atpt_ofcdc_sc_code: str, schul_nm: str) -> list[dict]:
        """
        교육청 코드와 학교명으로 학교를 검색합니다.
        """
        if self.school_data.empty:
            return []

        # 검색어에 대한 대소문자 무시를 위해 str.contains에 case=False 추가
        result = self.school_data[
            (self.school_data['시도교육청코드'] == atpt_ofcdc_sc_code) &
            (
                self.school_data['학교명'].str.contains(schul_nm, na=False) |
                self.school_data['영문학교명'].str.contains(schul_nm, na=False, case=False)
            )
        ].fillna(value="").to_dict(orient='records')
        return result

# 이 파일(school_search.py)은 app/services/에 위치합니다.
# 프로젝트 루트는 세 단계 위입니다.
DATA_FILE_PATH = Path(__file__).parent.parent.parent / "data" / "학교기본정보2024_11_30.csv"

# SchoolSearchService의 단일 인스턴스를 생성합니다.
# 이 인스턴스를 다른 모듈에서 가져와 사용합니다.
school_search_service = SchoolSearchService(DATA_FILE_PATH)
