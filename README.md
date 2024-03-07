# neisScheduleToICS
나이스 학사일정을 ICS(iCalendar) 파일로 변환해주는 프로그램입니다. 해당 프로그램을 이용해 더욱 쉽게 학교 학사일정을 캘린더에 추가하고, 알림을 받아 보실 수 있습니다.

## 사용법
- 나이스 학사일정 api를 이용해 학사일정을 json형식으로 가져옵니다.
- simple.js에 jsonData 변수에 json형식으로 가져온 학사일정을 넣어줍니다.
- `node index.js`를 실행하면 ics파일이 생성됩니다.
- 해당 파일을 개인적으로 사용하거나 서버에 배포하여 사용하시면 됩니다.

## 참고
<<<<<<< HEAD
- simple.js 파일은 나이스 학사일정 api와 연계되지 않고, json형식으로 가져온 학사일정을 ics 형식으로 변환합니다.
- 나이스 학사일정 api와 연계된 코드는 index.js 파일입니다. config.json파일을 수정하여 자신의 api키를 입력한 후 사용해 주세요.
=======

-   simple.js : 나이스 api 호출하지 않음
-   index.js : 나이스 api 호출
-   server.js : api 서버로 작동하는 코드

## simple.js 사용법

-   나이스 학사일정 api를 이용해 학사일정을 json형식으로 가져옵니다.
-   simple.js에 jsonData 변수에 json형식으로 가져온 학사일정을 넣어줍니다.
-   `node index.js`를 실행하면 ics파일이 생성됩니다.
-   해당 파일을 개인적으로 사용하거나 서버에 배포하여 사용하시면 됩니다.

## index.js 사용법

-   config.json에 나이스 api key와, 시도교육청코드, 행정표준코드를 입력합니다.
-   `node index.js`를 실행하면 ics파일이 생성됩니다.
-   해당 파일을 개인적으로 사용하거나 서버에 배포하여 사용하시면 됩니다.

## server.js 사용법

-   server.js를 실행하면 api 서버가 실행됩니다.
-   http://localhost:3007/api/calendar/school?ATPT_OFCDC_SC_CODE=시도교육청코드&SD_SCHUL_CODE=표준행정코드 로 접속하면 ./cache/시도교육청코드/표준행정코드.ics 파일이 캐싱되며, ics파일이 응답됩니다.
-   예시(부산소프트웨어마이스터고) /api/calendar/school?ATPT_OFCDC_SC_CODE=C10&SD_SCHUL_CODE=7150658
-   캐싱된 파일은 기본적으로 7일간 유효하며, 캐싱기간 동안 같은 학교의 학사일정을 요청하는 경우 같은 파일을 제공합니다.
-   캐싱기간을 변경하고 싶다면 server.js의 cacheTime 변수를 변경하면 됩니다.
>>>>>>> e2c44ce (Port change to 3007)
