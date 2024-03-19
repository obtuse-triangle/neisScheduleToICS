import fs from "fs";
import fetch from "node-fetch";
import config from "./config.json" assert { "type": "json" };

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
    let today = `${new Date().toISOString().slice(0, 4).replace(/-/g) + new Date().toISOString().slice(5, 7) + new Date().toISOString().slice(8, 10)}T${new Date()
        .toISOString()
        .slice(11, 13)}${new Date().toISOString().slice(14, 16)}${new Date().toISOString().slice(17, 19)}Z`;
    let ics = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//obtuse.kr//SchoolScheduleToICS//KO
CALSCALE:GREGORIAN
X-WR-CALNAME:${data.SchoolSchedule[1].row[0].SCHUL_NM} 학사일정
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
X-CREATED-TIME:${new Date().toISOString()}\n`;
    // X-WR-CALNAME:${data.SchoolSchedule[1].row[0].SCHUL_NM} 학사일정
    // LAST-MODIFIED:20231222T233358Z
    // LAST-MODIFIED:${today}

    data.SchoolSchedule.forEach((item) => {
        if (item.row) {
            item.row.forEach((event) => {
                const startDate = parseDate(event.AA_YMD);
                // const endDate = new Date(startDate);
                // endDate.setDate(endDate.getDate() + 1);

                ics += `BEGIN:VEVENT\n`;
                ics += `DTSTART;VALUE=DATE:${formatDate(startDate)}\n`;
                // ics += `DTEND:${formatDate(endDate)}T000000\n`;
                ics += `TRANSP:OPAQUE
DTSTAMP:${today}
X-MICROSOFT-CDO-BUSYSTATUS:BUSY
CLASS:PUBlIC
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
    ics += `END:VCALENDAR`;
    return ics;
}

var getSchoolSchedule = new Promise((resolve, reject) => {
    // const optionForSchedule = {
    //     uri: `https://open.neis.go.kr/hub/SchoolSchedule`,
    //     qs: {
    //         KEY: config.neisKey,
    //         Type: "json",
    //         ATPT_OFCDC_SC_CODE: config.ATPT_OFCDC_SC_CODE,
    //         SD_SCHUL_CODE: config.SD_SCHUL_CODE,
    //         // AA_YMD: new Date().toISOString().slice(0, 10).replace(/-/g, ""),
    //         // AA_YMD: 20240304,
    //         MLSV_FROM_YMD: new Date().toISOString().slice(0, 4).replace(/-/g) + "0101",
    //         MLSV_TO_YMD: String(Number(new Date().toISOString().slice(0, 4).replace(/-/g)) + 1) + "0101",
    //         pSize: 1000,
    //     },
    // };
    // get(optionForSchedule, (err, res, body) => {
    //     if (err) {
    //         console.log(err);
    //         reject(err);
    //     }
    //     const jsonData = JSON.parse(body);
    //     resolve(jsonData);
    // });
    fetch(
        `https://open.neis.go.kr/hub/SchoolSchedule?KEY=${config.neisKey}&Type=json&ATPT_OFCDC_SC_CODE=${config.ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE=${
            config.SD_SCHUL_CODE
        }&MLSV_FROM_YMD=${new Date().toISOString().slice(0, 4).replace(/-/g) + "0101"}&MLSV_TO_YMD=${
            String(Number(new Date().toISOString().slice(0, 4).replace(/-/g)) + 1) + "0101"
        }&pSize=1000`
    )
        .then((res) => res.json())
        .then((jsonData) => {
            resolve(jsonData);
        })
        .catch((error) => {
            reject(error);
        });
});

getSchoolSchedule
    .then((jsonData) => {
        const icsData = convertToICS(jsonData);
        fs.writeFileSync("events.ics", icsData, "utf8");
        console.log("ICS 파일이 생성되었습니다.");
    })
    .catch((error) => {
        console.error("오류가 발생했습니다:", error);
    });
