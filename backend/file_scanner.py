import os
from config import VALID_EXTENSIONS, EXCLUDE_DIRS

def get_code_files(base_path):
    files = []
    for root, dirs, filenames in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in filenames:
            ext = os.path.splitext(file)[1]
            if ext in VALID_EXTENSIONS:
                files.append(os.path.join(root, file))
    return files

def read_and_metadata(file_path, repo_name):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {
            "content": content,
            "filepath": file_path,
            "repo": repo_name,
            "language": os.path.splitext(file_path)[1][1:]
        }
    except Exception as e:
        print(f"⚠️ Skipping {file_path}: {e}")
        return None
