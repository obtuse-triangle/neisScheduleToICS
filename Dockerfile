# Python 3.12 이미지를 기반으로 합니다.
FROM python:3.12

# 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# 컨테이너의 8000번 포트를 외부에 노출합니다.
EXPOSE 8000

# 현재 디렉토리의 모든 파일을 컨테이너의 /app 디렉토리로 복사합니다.
COPY . /app

# config.json 파일이 있는지 확인합니다. 없으면 빌드에 실패합니다.
# RUN if [ ! -f config.json ]; then echo "neisAPI사용을 위해 config.json 파일이 필요합니다."; exit 1; fi
# 위 체크는 좋지만, 설정이 없는 경우에도 이미지를 빌드할 수 있도록 주석 처리합니다.
# 설정 파일은 실행 시점에 볼륨 마운트를 통해 제공하는 것이 더 유연한 방식입니다.

# requirements.txt에 명시된 파이썬 패키지들을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너가 시작될 때 실행될 명령어를 정의합니다.
# Uvicorn을 사용하여 app/main.py의 app 객체를 실행합니다.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
