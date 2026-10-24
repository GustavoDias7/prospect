import subprocess
import time
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

python = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")

process = subprocess.Popen(
    [str(python), "manage.py", "runserver", "127.0.0.1:8000"],
    cwd=BASE_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

driver = None

try:
    # Wait for Django to start.
    for _ in range(60):
        if process.poll() is not None:
            raise RuntimeError("Django server stopped unexpectedly")

        try:
            with urlopen("http://127.0.0.1:8000", timeout=1):
                break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError("Django server failed to start")

    options = Options()
    options.add_argument("--width=1240")
    options.add_argument("--height=740")
    driver = webdriver.Firefox(options=options)
    driver.get("http://127.0.0.1:8000")

    while driver.window_handles:
        time.sleep(1)

except Exception as e:
    print(f"Application closed: {e}")

finally:
    if driver:
        try:
            driver.quit()
        except Exception:
            pass

    # Windows: terminate Django and its child processes.
    subprocess.run(
        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )