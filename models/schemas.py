"""Pydantic models for API requests and responses."""
from pydantic import BaseModel


class SchoolSearch(BaseModel):
    """Model for school search requests."""
    ATPT_OFCDC_SC_CODE: str
    SCHUL_NM: str