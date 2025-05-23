from git import Repo
import os

def clone_repo(repo_url, clone_dir="cloned_repo"):
    if os.path.exists(clone_dir):
        print(f"{clone_dir} already exists. Deleting...")
        import shutil; shutil.rmtree(clone_dir)
    Repo.clone_from(repo_url, clone_dir)
    print(f"✅ Cloned {repo_url} into {clone_dir}")
    return clone_dir

clone_repo("https://github.com/jayanth920/t2s-s2t")