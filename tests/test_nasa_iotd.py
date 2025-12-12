import os
import sys
import types
from io import BytesIO

import pytest
from PIL import Image

import nasa_iotd as app


class DummyResp:
    def __init__(self, text=None, content=None):
        self.text = text
        self.content = content


def make_image_bytes(w, h, fmt="JPEG", color=(255, 0, 0)):
    img = Image.new("RGB", (w, h), color)
    buf = BytesIO()
    img.save(buf, fmt)
    return buf.getvalue()


@pytest.mark.parametrize(
    "src, expected",
    [
        ("https://www.nasa.gov/images/foo.jpg", "https://www.nasa.gov/images/foo.jpg"),
        ("//www.nasa.gov/images/foo.jpg", "https://www.nasa.gov/images/foo.jpg"),
        ("/images/foo.jpg", "https://www.nasa.gov/images/foo.jpg"),
    ],
)
def test_get_latest_image_url_parsing(monkeypatch, src, expected):
    html = f"""
    <html><body>
      <article>
        <img src=\"{src}\" />
      </article>
    </body></html>
    """

    def fake_get(_):
        return DummyResp(text=html)

    monkeypatch.setattr(app.requests, "get", fake_get)
    url = app.get_latest_image_url()
    assert url == expected


def test_resize_image_if_needed_downsizes_large_images():
    # Create a very large image
    big_bytes = make_image_bytes(8000, 5000)
    out_bytes = app.resize_image_if_needed(big_bytes)
    out_img = Image.open(BytesIO(out_bytes))
    w, h = out_img.size
    assert w <= app.MAX_WIDTH and h <= app.MAX_HEIGHT


def test_resize_image_if_needed_keeps_small_images():
    small_bytes = make_image_bytes(1920, 1080)
    out_bytes = app.resize_image_if_needed(small_bytes)
    # Should be unchanged
    assert out_bytes == small_bytes


def test_cleanup_old_images(tmp_path):
    # Prepare directory with three images; one should be kept
    keep = "keep.jpg"
    others = ["old1.jpg", "old2.jpg"]
    for name in [keep] + others:
        (tmp_path / name).write_bytes(b"x")

    app.cleanup_old_images(str(tmp_path), keep_history=False, keep_filename=keep)
    assert (tmp_path / keep).exists()
    for name in others:
        assert not (tmp_path / name).exists()


def test_set_wallpaper_is_called_with_bmp(monkeypatch, tmp_path):
    # Provide a small image
    img_bytes = make_image_bytes(640, 480)

    calls = {}

    class FakeUser32:
        def SystemParametersInfoW(self, action, uParam, path, winIni):
            # Check BMP path is created
            calls["args"] = (action, uParam, path, winIni)
            assert os.path.exists(path)
            assert path.lower().endswith(".bmp")
            return 1

    class FakeWindll:
        def __init__(self):
            self.user32 = FakeUser32()

    # Patch ctypes.windll on the module directly
    fake_ctypes = types.SimpleNamespace(windll=FakeWindll())
    monkeypatch.setattr(app, "ctypes", fake_ctypes)

    app.set_wallpaper(img_bytes)
    assert "args" in calls


def test_main_flow_creates_file_and_logs(monkeypatch, tmp_path):
    # Arrange temp dirs
    save_dir = tmp_path / "images"
    log_dir = tmp_path / "logs"

    test_url = "https://www.nasa.gov/images/test.jpg"
    test_img = make_image_bytes(100, 100)

    # Mock network and heavy side effects
    monkeypatch.setattr(app, "get_latest_image_url", lambda: test_url)
    monkeypatch.setattr(app, "download_img", lambda url: test_img)
    monkeypatch.setattr(app, "set_wallpaper", lambda data: None)

    # Simulate CLI args
    argv = [
        "prog",
        "--save-dir",
        str(save_dir),
        "--log-file",
        str(log_dir),
    ]
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    monkeypatch.setattr(sys, "argv", argv)

    app.main()

    # Assert image is saved
    saved_files = list(save_dir.glob("*.jpg"))
    assert len(saved_files) == 1

    # Assert log file exists and has some content
    log_file = log_dir / "iotdLog.log"
    assert log_file.exists()
    assert log_file.read_text("utf-8").strip() != ""
