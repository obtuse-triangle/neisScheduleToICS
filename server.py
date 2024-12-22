from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import requests
import os
import json
from datetime import datetime, timedelta
import re
import pandas as pd
from pydantic import BaseModel


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load config
with open("config.json", "r") as f:
  config = json.load(f)

# Load school data
with open("data/학교기본정보2024_11_30.csv", "r", encoding='cp949') as f:
  school_data = pd.read_csv(f)
  print(school_data.info())
# Helper functions


def parse_date(date_string: str):
  year = int(date_string[:4])
  month = int(date_string[4:6]) - 1
  day = int(date_string[6:8])
  return datetime(year, month + 1, day)


def format_date(date: datetime):
  return date.strftime("%Y%m%d")

# 나이스 학사일정 ICS형식으로 변환


def convert_to_ics(data):
  today = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
  ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//obtuse.kr//SchoolScheduleToICS//KO
CALSCALE:GREGORIAN
X-WR-CALNAME:{data['SchoolSchedule'][1]['row'][0]['SCHUL_NM']} 학사일정
X-WR-TIMEZONE:Asia/Seoul
BEGIN:VTIMEZONE
TZID:Asia/Seoul
TZURL:https://www.tzurl.org/zoneinfo-outlook/Asia/Seoul
X-LIC-LOCATION:Asia/Seoul
BEGIN:STANDARD
DTSTART:19700101T000000
TZNAME:KST
TZOFFSETFROM:+0900
TZOFFSETTO:+0900
END:STANDARD
END:VTIMEZONE
X-CREATED-TIME:{datetime.utcnow().isoformat()}\n"""

  for item in data['SchoolSchedule']:
    if 'row' in item:
      for event in item['row']:
        start_date = parse_date(event['AA_YMD'])
        ics += f"""BEGIN:VEVENT
DTSTART;VALUE=DATE:{format_date(start_date)}
TRANSP:OPAQUE
DTSTAMP:{today}
X-MICROSOFT-CDO-BUSYSTATUS:BUSY
CLASS:PUBLIC
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:{event['EVENT_NM']}
TRIGGER:-P1D
END:VALARM
SUMMARY:{event['EVENT_NM']}
DESCRIPTION:{event['EVENT_CNTNT']}
LOCATION:{event['SCHUL_NM']}
END:VEVENT\n"""
  ics += "END:VCALENDAR"
  return ics


def ensure_directory_existence(file_path):
  dirname = os.path.dirname(file_path)
  if not os.path.exists(dirname):
    os.makedirs(dirname)

# 나이스 학사일정 API 호출


async def get_school_schedule(ATPT_OFCDC_SC_CODE: str, SD_SCHUL_CODE: int):
  url = f"https://open.neis.go.kr/hub/SchoolSchedule?KEY={config['neisKey']}&Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_FROM_YMD={datetime.now().year}0101&MLSV_TO_YMD={(datetime.now().year + 1)}0101&pSize=1000"
  print(url)
  response = requests.get(url)
  if response.status_code == 200:
    return response.json()
  else:
    raise HTTPException(status_code=response.status_code,
                        detail="Error fetching data from NEIS server")


@app.get("/school")
async def get_school(ATPT_OFCDC_SC_CODE: str, SD_SCHUL_CODE: int):
  if ATPT_OFCDC_SC_CODE is None or SD_SCHUL_CODE is None:
    return {"message": "시도교육청 코드와 학교 코드를 입력해주세요. 예) /school?ATPT_OFCDC_SC_CODE=C10&SD_SCHUL_CODE=7150658"}

  file_path = os.path.join("cache", ATPT_OFCDC_SC_CODE, f"{SD_SCHUL_CODE}.ics")

  if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf8") as file:
      content = file.read()
      match = re.search(
        r'X-CREATED-TIME:(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}.\d{3}Z', content)

      if match and datetime.now() - datetime.fromisoformat(match.group(1)) < timedelta(days=config['cache_day']):
        return FileResponse(file_path, media_type='text/calendar', filename='school_schedule.ics')

  jsonData = await get_school_schedule(ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE)
  ics_data = convert_to_ics(jsonData)
  ensure_directory_existence(file_path)

  with open(file_path, "w", encoding="utf8") as file:
    file.write(ics_data)

  return FileResponse(file_path, media_type='text/calendar', filename='school_schedule.ics')


@app.get("/")
async def index(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})


class SchoolSearch(BaseModel):
  ATPT_OFCDC_SC_CODE: str
  SCHUL_NM: str

# 학교 검색 API


@app.post("/search")
async def schoolSearch(schoolSearch: SchoolSearch):
  ATPT_OFCDC_SC_CODE = schoolSearch.ATPT_OFCDC_SC_CODE
  SCHUL_NM = schoolSearch.SCHUL_NM
  result = school_data[(school_data['시도교육청코드'] == ATPT_OFCDC_SC_CODE) & (
    school_data['학교명'].str.contains(SCHUL_NM, na=False) | school_data['영문학교명'].str.contains(SCHUL_NM, na=False))].fillna(value="").to_dict(orient='records')
  return JSONResponse(content=result)
