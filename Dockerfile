FROM python:3.12
WORKDIR /app
EXPOSE 8000
COPY . /app
RUN if [ ! -f config.json ]; then echo "neisAPI사용을 위해 config.json 파일이 필요합니다."; exit 1; fi
RUN pip install -r requirements.txt
CMD ["fastapi", "run", "--host", "0.0.0.0", "server.py"]
