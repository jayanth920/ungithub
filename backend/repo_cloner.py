import subprocess
import shutil
import os
import logging

logger = logging.getLogger("uvicorn")

def clone_repo(repo_url):
    repo_name = repo_url.rstrip("/").split("/")[-1]
    if os.path.exists(repo_name):
        shutil.rmtree(repo_name)
    subprocess.run(["git", "clone", repo_url, repo_name])
    logger.info(f"✅ Cloned {repo_url} into {repo_name}")
    return repo_name
