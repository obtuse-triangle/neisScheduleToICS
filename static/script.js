document.addEventListener("DOMContentLoaded", () => {
  const searchForm = document.querySelector("form");
  const schoolTable = document.querySelector("table");
  const schoolTableBody = schoolTable.querySelector("tbody");
  const popup = document.querySelector(".popup1");

  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const atptCode = e.target.ATPT_OFCDC_SC_CODE.value;
    const schoolName = e.target.SCHUL_NM.value;

    if (!schoolName) {
      alert("학교명을 입력해주세요.");
      return;
    }

    // Show loading indicator if you have one
    schoolTable.hidden = false;
    schoolTableBody.innerHTML = '<tr><td colspan="5">검색 중...</td></tr>';

    fetch("./search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ATPT_OFCDC_SC_CODE: atptCode,
        SCHUL_NM: schoolName,
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        schoolTableBody.innerHTML = ""; // Clear previous results or loading indicator
        if (data.length === 0) {
          schoolTableBody.innerHTML = '<tr><td colspan="5">검색 결과가 없습니다.</td></tr>';
          return;
        }
        data.forEach((school) => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${school["학교명"]}</td>
            <td>${school["시도교육청코드"]}</td>
            <td>${school["행정표준코드"]}</td>
            <td>${school["도로명주소"]}</td>
            <td><button class="add-calendar-btn" data-atpt-code="${school["시도교육청코드"]}" data-school-code="${school["행정표준코드"]}">추가</button></td>
          `;
          schoolTableBody.appendChild(tr);
        });
      })
      .catch((error) => {
        schoolTableBody.innerHTML = `<tr><td colspan="5">오류가 발생했습니다: ${error.message}</td></tr>`;
        console.error("Fetch error:", error);
      });
  });

  // Event delegation for dynamically created buttons
  schoolTableBody.addEventListener("click", (e) => {
    if (e.target && e.target.classList.contains("add-calendar-btn")) {
      const atptCode = e.target.dataset.atptCode;
      const schoolCode = e.target.dataset.schoolCode;
      openPopup(atptCode, schoolCode);
    }
  });

  function openPopup(atptCode, schoolCode) {
    // Note: The base URL might need to be configurable
    const calendarUrl = `/school?ATPT_OFCDC_SC_CODE=${atptCode}&SD_SCHUL_CODE=${schoolCode}`;
    const webcalUrl = `webcal://${window.location.host}${calendarUrl}`;
    const httpsUrl = `https://${window.location.host}${calendarUrl}`;

    // Attempt to open the webcal link automatically
    window.location.href = webcalUrl;

    // Show the popup with manual instructions
    popup.style.opacity = 1;
    popup.style.pointerEvents = "auto";
    popup.querySelector("code").innerText = httpsUrl;
  }

  // Close popup logic
  popup.addEventListener("click", (e) => {
    // Close if the click is on the background overlay itself, not on its children
    if (e.target === e.currentTarget) {
      popup.style.opacity = 0;
      popup.style.pointerEvents = "none";
    }
  });
});
