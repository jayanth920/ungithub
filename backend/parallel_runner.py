import subprocess
from concurrent.futures import ProcessPoolExecutor

# Number of parallel runs
N = 2

# Repo URL to process
repo_url = "https://github.com/jayanth920/t2s-s2t"

def run_process():
    subprocess.run(["python", "main.py", repo_url])

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=N) as executor:
        futures = [executor.submit(run_process) for _ in range(N)]
        for future in futures:
            future.result()
