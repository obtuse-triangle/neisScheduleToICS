"""File system utilities."""
import os


def ensure_directory_existence(file_path: str) -> None:
    """Ensure the directory for the given file path exists."""
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)