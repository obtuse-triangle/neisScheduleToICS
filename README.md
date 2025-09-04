# 나이스 학사일정 ICS 변환기 (Python/FastAPI)

나이스(NEIS) 교육정보 공공데이터 포털의 학사일정 정보를 조회하여 iCalendar(.ics) 파일로 변환해주는 API 서버입니다. 이 프로그램을 통해 학교 학사일정을 구글 캘린더, 애플 캘린더 등에서 손쉽게 구독하고 알림을 받을 수 있습니다.

기존 Node.js 기반 코드를 Python FastAPI를 사용하여 재작성하고, 유지보수가 용이하도록 프로젝트 구조를 개선했습니다.

## 주요 기능

-   **학교 검색**: 시도교육청과 학교명으로 학교를 검색하고 표준 코드를 조회합니다.
-   **ICS 변환**: 조회된 학사일정을 iCalendar(.ics) 형식으로 변환하여 제공합니다.
-   **캐싱**: 한 번 조회된 학사일정은 `.ics` 파일로 캐시하여 이후 요청 시 빠르게 응답합니다. (기본 7일 유지)
-   **웹 인터페이스**: 간단한 웹 페이지를 통해 학교를 검색하고 캘린더 구독 링크를 생성할 수 있습니다.

## 프로젝트 구조

```
/
|-- app/                  # FastAPI 소스 코드
|   |-- main.py           # API 엔드포인트 및 앱 설정
|   |-- core/             # 설정(config) 관리
|   |-- models/           # Pydantic 데이터 모델
|   |-- services/         # 비즈니스 로직 (NEIS API, ICS 변환 등)
|   |-- utils/            # 유틸리티 함수
|-- data/                 # 학교 기본 정보 CSV 파일
|-- static/               # CSS, JavaScript 등 정적 파일
|-- templates/            # HTML 템플릿 파일
|-- cache/                # 생성된 ICS 파일 캐시 (자동 생성)
|-- Dockerfile            # Docker 이미지 빌드 설정
|-- requirements.txt      # Python 의존성 목록
|-- config.json.example   # 설정 파일 예시 (직접 config.json으로 생성해야 함)
|-- README.md             # 프로젝트 설명서
```

## 사용법

### 1. 사전 준비

-   Python 3.11 이상
-   [나이스 교육정보 공공데이터 포털](https://open.neis.go.kr/)에서 **학사일정 API 활용 신청** 후 인증키(API Key) 발급

### 2. 설정

1.  프로젝트 루트 디렉토리에 `config.json` 파일을 생성합니다.
2.  아래 내용을 참고하여 파일을 작성합니다. `YOUR_API_KEY` 부분에 발급받은 인증키를 입력하세요.

    ```json
    {
      "neisKey": "YOUR_API_KEY",
      "cache_day": 7
    }
    ```

### 3. 로컬 환경에서 실행

1.  필요한 Python 패키지를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

2.  Uvicorn을 사용하여 FastAPI 애플리케이션을 실행합니다.
    ```bash
    uvicorn app.main:app --reload
    ```
    `--reload` 옵션은 코드 변경 시 서버를 자동으로 재시작해주는 개발용 옵션입니다.

3.  웹 브라우저에서 `http://127.0.0.1:8000`으로 접속하여 웹 인터페이스를 확인합니다.

### 4. Docker를 사용하여 실행

1.  Docker 이미지를 빌드합니다.
    ```bash
    docker build -t neis-ics-converter .
    ```

2.  빌드된 이미지를 사용하여 컨테이너를 실행합니다. `config.json` 파일을 컨테이너 내부로 마운트해야 합니다.
    ```bash
    docker run -d -p 8000:8000 -v $(pwd)/config.json:/app/config.json --name neis-calendar neis-ics-converter
    ```

3.  웹 브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.

## API 엔드포인트

-   `GET /`: 메인 웹 페이지
-   `POST /search`: 학교 검색
-   `GET /school`: 학사일정 ICS 파일 다운로드
    -   **쿼리 파라미터**:
        -   `ATPT_OFCDC_SC_CODE` (문자열): 시도교육청코드
        -   `SD_SCHUL_CODE` (정수): 학교표준코드

## 기존 코드 (Legacy)

-   기존에 Node.js로 작성된 코드들은 `.legacy` 디렉토리에 보관되어 있습니다.
