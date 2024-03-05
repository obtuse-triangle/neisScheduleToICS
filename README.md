# neisScheduleToICS
나이스 학사일정을 ICS(iCalendar) 파일로 변환해주는 프로그램입니다. 해당 프로그램을 이용해 더욱 쉽게 학교 학사일정을 캘린더에 추가하고, 알림을 받아 보실 수 있습니다.

## 사용법
- 나이스 학사일정 api를 이용해 학사일정을 json형식으로 가져옵니다.
- simple.js에 jsonData 변수에 json형식으로 가져온 학사일정을 넣어줍니다.
- `node index.js`를 실행하면 ics파일이 생성됩니다.
- 해당 파일을 개인적으로 사용하거나 서버에 배포하여 사용하시면 됩니다.

## 참고
- simple.js 파일은 나이스 학사일정 api와 연계되지 않고, json형식으로 가져온 학사일정을 ics 형식으로 변환합니다.
- 나이스 학사일정 api와 연계된 코드는 index.js 파일입니다. config.json파일을 수정하여 자신의 api키를 입력한 후 사용해 주세요.