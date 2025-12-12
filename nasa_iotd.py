"""
Script NASA Image of the Day — portable, configurable, multi-user friendly

Usage :
  python nasa_iotd.py
  python nasa_iotd.py --save-dir "C:/Images" --log-file "C:/Logs/iotd.log" --keep-history
"""

import os
import requests
from bs4 import BeautifulSoup
import argparse
import ctypes
from PIL import Image
from io import BytesIO
from datetime import datetime
import tempfile

# ---------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------
NASA_URL = "https://www.nasa.gov/image-of-the-day/"
MAX_WIDTH = 3840
MAX_HEIGHT = 2160

# Emplacements par défaut portables (dans AppData)
DEFAULT_BASE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.getcwd()), "nasa_iotd")
DEFAULT_SAVE_DIR = os.path.join(DEFAULT_BASE_DIR, "images")
DEFAULT_LOG_FILE = DEFAULT_BASE_DIR

os.makedirs(DEFAULT_SAVE_DIR, exist_ok=True)

# Temp log buffer
current_execution_logs = []

# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    print(line, end="")
    current_execution_logs.append(line)


def flush_logs_to_file(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "iotdLog.log")

    new_block = "".join(current_execution_logs)
    old_logs = ""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            old_logs = f.read()

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(new_block + "\n" + old_logs)


# ---------------------------------------------------------
# IMAGE PROCESSING
# ---------------------------------------------------------
def resize_image_if_needed(img_bytes):
    img = Image.open(BytesIO(img_bytes))
    width, height = img.size

    if width <= MAX_WIDTH and height <= MAX_HEIGHT:
        log(f"Image already correct ({width}x{height}), no reduction.")
        return img_bytes

    log(f"4K Reduction : {width}x{height} → max {MAX_WIDTH}x{MAX_HEIGHT}")
    img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)
    new_size = img.size
    log(f"New size : {new_size[0]}x{new_size[1]}")

    output = BytesIO()
    img.save(output, format=img.format or "JPEG")
    return output.getvalue()


def save_img(img_bytes, url, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    filename = url.split('/')[-1]
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "wb") as f:
        f.write(img_bytes)
    log(f"Image saved : {save_path}")
    return save_path


# ---------------------------------------------------------
# WALLPAPER
# ---------------------------------------------------------
def set_wallpaper(img_bytes):
    log("Applying the wallpaper...")
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    bmp_path = os.path.join(tempfile.gettempdir(), "iotd_wallpaper.bmp")
    img.save(bmp_path, "BMP")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, bmp_path, 3)
    log("Wallpaper applied.")


# ---------------------------------------------------------
# NETWORK & PARSING
# ---------------------------------------------------------
def get_latest_image_url():
    log("Retrieving the NASA page...")
    html = requests.get(NASA_URL).text
    soup = BeautifulSoup(html, "html.parser")

    img = soup.select_one("article img")
    if not img:
        raise Exception("The image could not be found on the NASA page.")

    src = img.get("src")
    if src.startswith("//"):
        src = "https:" + src
    elif src.startswith("/"):
        src = "https://www.nasa.gov" + src

    log(f"Image URL detected : {src}")
    return src


def download_img(url):
    log(f"Downloading the image...")
    img_data = requests.get(url).content
    return resize_image_if_needed(img_data)


# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------
def cleanup_old_images(save_dir, keep_history, keep_filename):
    if keep_history:
        return

    for file in os.listdir(save_dir):
        if file != keep_filename:
            try:
                os.remove(os.path.join(save_dir, file))
                log(f"Old image deleted: {file}")
            except Exception as e:
                log(f"Error deletion {file} : {e}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    log("---- Execution begins ----")
    parser = argparse.ArgumentParser(description="NASA Image of the Day Downloader")
    parser.add_argument("--save-dir", type=str, default=DEFAULT_SAVE_DIR,
                        help="Image save path (default: AppData)")
    parser.add_argument("--log-file", type=str, default=DEFAULT_LOG_FILE,
                        help="Log file path (default: AppData)")
    parser.add_argument("--keep-history", action="store_true",
                        help="Keep all the images instead of just one")
    args = parser.parse_args()

    save_dir = args.save_dir
    log_file_dir = args.log_file
    keep_history = args.keep_history

    try:
        img_url = get_latest_image_url()
        filename = img_url.split('/')[-1]
        save_path = os.path.join(save_dir, filename)

        if not os.path.exists(save_path):
            img_bytes = download_img(img_url)
            save_img(img_bytes, img_url, save_dir)
            set_wallpaper(img_bytes)
        else:
            log(f"Already existing image: {filename}")
            with open(save_path, "rb") as f:
                set_wallpaper(f.read())

        cleanup_old_images(save_dir, keep_history, filename)

    except Exception as e:
        log(f"❌ ERROR : {e}")

    finally:
        log("---- End of execution ----")
        flush_logs_to_file(log_file_dir)


if __name__ == "__main__":
    main()
