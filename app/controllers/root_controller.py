from fastapi import Request
from fastapi.templating import Jinja2Templates

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

async def get_index_page(request: Request):
    """
    메인 페이지(index.html)를 렌더링하여 반환합니다.
    """
    return templates.TemplateResponse("index.html", {"request": request})
