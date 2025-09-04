"""Main application entry point."""
from fastapi import FastAPI, Request

from api import get_school, index, school_search
from models import SchoolSearch


app = FastAPI()


# Register routes
@app.get("/school")
async def school_endpoint(ATPT_OFCDC_SC_CODE: str, SD_SCHUL_CODE: int):
    """Get school schedule endpoint."""
    return await get_school(ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE)


@app.get("/")
async def index_endpoint(request: Request):
    """Index page endpoint."""
    return await index(request)


@app.post("/search")
async def search_endpoint(school_search_data: SchoolSearch):
    """School search endpoint."""
    return await school_search(school_search_data)