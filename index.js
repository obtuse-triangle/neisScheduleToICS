const fs = require("fs");

// "YYYYMMDD" 형식의 문자열을 Date 객체로 변환하는 함수
function parseDate(dateString) {
    const year = parseInt(dateString.substr(0, 4));
    const month = parseInt(dateString.substr(4, 2)) - 1; // 월은 0부터 시작하므로 -1 해줍니다.
    const day = parseInt(dateString.substr(6, 2));
    return new Date(year, month, day);
}

// 주어진 날짜를 YYYYMMDD 형식의 문자열로 변환하는 함수
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}${month}${day}`;
}

// JSON 데이터에서 이벤트를 ICS 형식으로 변환하는 함수
function convertToICS(data) {
    let ics = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//obtuse.kr//SchoolScheduleToICS//KO
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Asia/Seoul
LAST-MODIFIED:20231222T233358Z
TZURL:https://www.tzurl.org/zoneinfo-outlook/Asia/Seoul
X-LIC-LOCATION:Asia/Seoul
BEGIN:STANDARD
TZNAME:KST
TZOFFSETFROM:+0900
TZOFFSETTO:+0900
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE\n`;
    // X-WR-CALNAME:${data.SchoolSchedule[1].row[0].SCHUL_NM} 학사일정

    data.SchoolSchedule.forEach((item) => {
        if (item.row) {
            item.row.forEach((event) => {
                const startDate = parseDate(event.AA_YMD);
                const endDate = new Date(startDate);
                endDate.setDate(endDate.getDate() + 1);

                ics += `BEGIN:VEVENT\n`;
                ics += `DTSTART;VALUE=DATE:${formatDate(startDate)}\n`;
                // ics += `DTEND:${formatDate(endDate)}T000000\n`;
                ics += `TRANSP:OPAQUE
X-MICROSOFT-CDO-BUSYSTATUS:BUSY
CLASS:PRIVATE
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:${event.EVENT_NM}
TRIGGER:-P1D
END:VALARM\n`;
                ics += `SUMMARY:${event.EVENT_NM}\n`;
                ics += `DESCRIPTION:${event.EVENT_CNTNT}\n`;
                ics += `LOCATION:${event.SCHUL_NM}\n`;
                ics += `END:VEVENT\n`;
            });
        }
    });

    return ics;
}

// 나이스에서 받아온 학사일정 JSON 데이터
const jsonData = {
    SchoolSchedule: [
        {
            head: [
                {
                    list_total_count: 1,
                },
                {
                    RESULT: {
                        CODE: "INFO-000",
                        MESSAGE: "정상 처리되었습니다.",
                    },
                },
            ],
        },
        {
            row: [
                {
                    ATPT_OFCDC_SC_CODE: "C10",
                    SD_SCHUL_CODE: "7150658",
                    AY: "2024",
                    AA_YMD: "20240304",
                    ATPT_OFCDC_SC_NM: "부산광역시교육청",
                    SCHUL_NM: "부산소프트웨어마이스터고등학교",
                    DGHT_CRSE_SC_NM: "주간",
                    SCHUL_CRSE_SC_NM: "고등학교",
                    EVENT_NM: "입학식",
                    EVENT_CNTNT: "",
                    ONE_GRADE_EVENT_YN: "Y",
                    TW_GRADE_EVENT_YN: "Y",
                    THREE_GRADE_EVENT_YN: "Y",
                    FR_GRADE_EVENT_YN: "*",
                    FIV_GRADE_EVENT_YN: "*",
                    SIX_GRADE_EVENT_YN: "*",
                    SBTR_DD_SC_NM: "해당없음",
                    LOAD_DTM: "20240305",
                },
            ],
        },
    ],
};

// JSON 데이터를 ICS로 변환
const icsData = convertToICS(jsonData);

// 변환된 ICS를 파일로 저장
fs.writeFileSync("events.ics", icsData, "utf8");
console.log("ICS 파일이 생성되었습니다.");
