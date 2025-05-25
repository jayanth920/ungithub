import subprocess
import shutil
import os
import logging

logger = logging.getLogger("uvicorn")

def clone_repo(repo_url, dest_dir=None):
    if dest_dir is None:
        repo_name = repo_url.rstrip("/").split("/")[-1]
        dest_dir = repo_name

    # Delete if already exists
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    # Clone into the destination directory
    subprocess.run(["git", "clone", repo_url, dest_dir], check=True)
    logger.info(f"✅ Cloned {repo_url} into {dest_dir}")
    return dest_dir
