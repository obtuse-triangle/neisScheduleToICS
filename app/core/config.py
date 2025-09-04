import json
from pathlib import Path

# 프로젝트 루트 디렉토리를 기준으로 config.json 경로 설정
# 이 파일(config.py)은 app/core/ 에 있으므로, 두 단계 상위 디렉토리로 이동해야 합니다.
CONFIG_FILE_PATH = Path(__file__).parent.parent.parent / "config.json"

def load_config() -> dict:
    """
    config.json 파일을 로드하여 설정을 반환합니다.
    파일이 존재하지 않을 경우 FileNotFoundError를 발생시킵니다.
    """
    if not CONFIG_FILE_PATH.exists():
        raise FileNotFoundError(f"Config file not found at: {CONFIG_FILE_PATH}")

    with open(CONFIG_FILE_PATH, "r") as f:
        config = json.load(f)
    return config

# 전역 설정 객체
# 애플리케이션 시작 시 한 번만 로드됩니다.
try:
    settings = load_config()
except FileNotFoundError as e:
    # 애플리케이션이 config.json 없이 시작되지 않도록 처리
    print(f"Error: {e}")
    print("Please create a 'config.json' file in the root directory.")
    # 실제 운영 환경에서는 여기서 시스템을 종료하거나,
    # 기본 설정을 사용하는 등의 처리를 할 수 있습니다.
    settings = {
        "neisKey": "YOUR_API_KEY_HERE",
        "cache_day": 7
    }
