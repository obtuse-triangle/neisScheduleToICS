from pydantic import BaseModel

class SchoolSearch(BaseModel):
  """
  학교 검색 API의 요청 본문을 위한 Pydantic 모델입니다.
  """
  ATPT_OFCDC_SC_CODE: str
  SCHUL_NM: str
