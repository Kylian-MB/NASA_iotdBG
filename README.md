NASA Image of the Day (Windows wallpaper helper)

Overview
This small Python script downloads NASA’s Image of the Day and sets it as the Windows desktop wallpaper. It keeps logs in a portable location and can either keep only the latest image or preserve a history of downloaded images.

Key features
- Fetch the latest image from NASA’s Image of the Day page
- Optional resize down to a 4K-friendly maximum (3840×2160)
- Save images to a configurable folder
- Set the Windows wallpaper automatically
- Prepend-in-place logging to a portable log file

Stack / Technology
- Language: Python (single-file script)
- Libraries:
  - requests (HTTP)
  - beautifulsoup4 (HTML parsing)
  - Pillow (image processing)
  - Standard library: argparse, os, io, datetime, tempfile, ctypes, etc.
- Platform: Windows (wallpaper is applied via `ctypes` and `SystemParametersInfoW`)
- Package manager: pip; dependencies tracked in `requirements.txt`.

Project structure
- nasa_iotd.py — main script with `main()` entry point

Entry point and usage
- Entry point: `if __name__ == "__main__": main()` inside `nasa_iotd.py`.
- Run from a terminal:
  - Basic: `python nasa_iotd.py`
  - With options:
    - `--save-dir <path>`: directory where images are saved (default is under `%LOCALAPPDATA%\nasa_iotd\images`).
    - `--log-file <path>`: directory where the log file `iotdLog.log` is stored (default is `%LOCALAPPDATA%\nasa_iotd`).
    - `--keep-history`: keep all images; if omitted, old images are removed and only the latest is kept.

Examples
```
python nasa_iotd.py
python nasa_iotd.py --save-dir "C:\Images" --log-file "C:\Logs" --keep-history
```

Requirements
- Python 3.x on Windows
- Internet connectivity to reach `https://www.nasa.gov/image-of-the-day/`
- Packages (install via pip):
  - requests
  - beautifulsoup4
  - pillow

Installation
- Optional (recommended) create and activate a virtual environment on Windows:
```
python -m venv .venv
.venv\Scripts\activate
```
- Install dependencies from `requirements.txt`:
```
pip install -r requirements.txt
```

Download
- Windows executable (.exe):
  - Latest build: https://github.com/Kylian-MB/NASA_iotdBG/releases/latest/download/NASA-IOTD.exe
  - Note: Windows SmartScreen may warn about unsigned executables. Click "More info" > "Run anyway" if you trust this project.

Virtual environment guide (Windows)
This project is simple, but using a virtual environment keeps dependencies isolated and avoids system‑wide changes. Below is a concise guide tailored for Windows.

1) Create a venv in the project folder
```
python -m venv .venv
```

2) Activate the venv
- PowerShell (recommended):
```
.venv\Scripts\Activate.ps1
```
- CMD:
```
.venv\Scripts\activate.bat
```
When activated, your prompt will show `(.venv)`.

3) First‑time tips
- If PowerShell blocks script execution, start a new PowerShell window and run:
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
- Upgrade pip (optional):
```
python -m pip install --upgrade pip
```

4) Install project dependencies
```
pip install -r requirements.txt
```

5) Run the script while venv is active
```
python nasa_iotd.py
```

6) Deactivate the venv when you are done
```
deactivate
```

7) Update dependencies (optional)
- After adding or upgrading packages, you can update `requirements.txt`:
```
pip freeze > requirements.txt
```

8) Remove the venv (optional)
- Close terminals using it, then delete the `.venv` folder.

Notes
- If you have multiple Python versions, replace `python` with the full path (for example, `C:\Python311\python.exe`).
- In VS Code, when the venv is created inside the workspace as `.venv`, the Python extension usually auto‑detects it; otherwise, pick it from the interpreter selector.

Environment variables
- `LOCALAPPDATA` (Windows): used to build the default portable base directory `%LOCALAPPDATA%\nasa_iotd` for images and logs when no custom paths are provided.

How it works (brief)
1. Downloads NASA’s Image of the Day page: `https://www.nasa.gov/image-of-the-day/`.
2. Parses the first `<article> <img>` element to extract the image URL.
3. Downloads the image and resizes it if it exceeds 3840×2160.
4. Saves the image to the configured `--save-dir`.
5. Sets the Windows wallpaper by converting the image to BMP and calling `SystemParametersInfoW`.
6. Writes execution logs to `iotdLog.log`, prepending the latest run at the top.

Logs and files
- Log file: `iotdLog.log` in the directory specified by `--log-file` (or `%LOCALAPPDATA%\nasa_iotd` by default).
- Images: stored in the directory specified by `--save-dir` (or `%LOCALAPPDATA%\nasa_iotd\images` by default).
- When `--keep-history` is not provided, previously downloaded images (other than the current one) are deleted after a successful run.

Tests
- Test runner: `pytest`.
- Run locally:
  1) Install dev tool: `pip install pytest`
  2) From the project root, run: `pytest -q`
  
What’s covered
- HTML parsing of the Image of the Day URL resolution (`get_latest_image_url`).
- Image resize behavior to stay within 3840×2160.
- Cleanup of old images when history is not kept.
- Wallpaper application is exercised with a mocked Windows API (no real desktop change).
- A light end-to-end flow through `main()` with network and OS side-effects mocked.

Continuous Integration
- A simple GitHub Actions workflow runs tests on `windows-latest` for pushes and pull requests. See `.github/workflows/ci.yml`.

Known limitations
- Windows-only wallpaper application (uses `ctypes.windll.user32.SystemParametersInfoW`).
- The HTML parsing is minimal and assumes an `<article> <img>` exists on the NASA IOTD page; page structure changes could break the fetch.
- No retry/backoff for network requests; transient failures will log an error.

Troubleshooting
- If the wallpaper does not change:
  - Confirm you are running on Windows.
  - Check that the script has permission to write to the temporary directory and your chosen `--save-dir`.
  - Review `iotdLog.log` in the `--log-file` directory for errors.
- If parsing fails with messages like “The image could not be found on the NASA page.”, the page structure may have changed. Consider updating the CSS selector used in `get_latest_image_url()`.

License
- This project’s source code is licensed under the MIT License. See the `LICENSE` file for full terms.
- Note: The NASA Image of the Day content is subject to NASA’s own usage and media guidelines; your code license does not grant rights to NASA imagery.

Changelog
- 2025-12-12: Added download link to Windows executable in the README.
- 2025-12-12: Added unit tests (pytest) and GitHub Actions CI workflow (Windows).
- 2025-12-12: Added a detailed virtual environment guide to the README.
- 2025-12-12: Added LICENSE (MIT) and updated README (License section).
- 2025-12-12: Added `requirements.txt` and updated README (installation and stack notes). 
- 2025-12-12: Initial README added based on current code.
