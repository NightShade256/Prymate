import os
import shutil
import subprocess
import tarfile
import urllib.request

from pathlib import Path

PYODIDE_URL = "https://github.com/pyodide/pyodide/releases/download/0.28.3/pyodide-core-0.28.3.tar.bz2"
ROOT_DIR = Path(__file__).parent.resolve()
PUBLIC_DIR = ROOT_DIR / "public"
DOWNLOAD_PATH = PUBLIC_DIR / "pyodide-core-0.28.3.tar.bz2"
PYODIDE_DIR = PUBLIC_DIR / "pyodide"


def main():
    PUBLIC_DIR.mkdir(exist_ok=True)

    print(f"[-] Downloading Pyodide artifacts from {PYODIDE_URL}")
    urllib.request.urlretrieve(PYODIDE_URL, DOWNLOAD_PATH)
    print("[-] Download complete")

    print(f"[-] Extracting to {PYODIDE_DIR}")
    if PYODIDE_DIR.exists():
        shutil.rmtree(PYODIDE_DIR)

    with tarfile.open(DOWNLOAD_PATH, "r:bz2") as tar:
        tar.extractall(PUBLIC_DIR, filter=tarfile.data_filter)

    os.remove(DOWNLOAD_PATH)
    print("[-] Extraction complete")

    print("[-] Building wheel using uv build (prymate)")
    subprocess.run(
        ["uv", "build", "--wheel", "-o", str(PUBLIC_DIR)],
        cwd=ROOT_DIR,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    print("[-] Wheel build complete")


if __name__ == "__main__":
    main()
