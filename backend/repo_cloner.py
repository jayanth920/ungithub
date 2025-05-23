from git import Repo
import os
import shutil

def clone_repo(repo_url, clone_dir="cloned_repo"):
    if os.path.exists(clone_dir):
        print(f"{clone_dir} already exists. Deleting...")
        shutil.rmtree(clone_dir)
    Repo.clone_from(repo_url, clone_dir)
    print(f"✅ Cloned {repo_url} into {clone_dir}")
    return clone_dir
