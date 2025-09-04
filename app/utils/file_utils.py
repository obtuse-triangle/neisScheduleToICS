import os

def ensure_directory_existence(file_path: str):
    """
    주어진 파일 경로의 디렉토리가 존재하지 않으면 생성합니다.
    """
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
