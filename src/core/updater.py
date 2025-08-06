import hashlib
import re
import time

import requests
from PySide6.QtCore import qDebug, qWarning, QCoreApplication, QDir, qInfo, QFileInfo, \
    qCritical, Qt
from PySide6.QtWidgets import QMessageBox, QProgressDialog, QApplication
from packaging import version
from tqdm import tqdm

from src.core.app_path_utils import _get_desktop_path
from src.core.process_utils import _stop_and_run_new_exe
from src.core.ui_utils import close_splash_screen
from src.name_version import GITHUB_REPO_NAME, APP_NAME, APP_VERSION

_ID_TAG = "[UPDATER]"


def _format_eta(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"


def _get_latest_release_data(session: requests.Session, url: str) -> dict:
    try:
        response = session.get(url, timeout=5, allow_redirects=False, verify=True)
        if not response.url.startswith("https://"):
            message = QCoreApplication.translate("updater", "Insecure redirect detected.")
            qWarning(f"{_ID_TAG} {message}")
            return {}
        response.raise_for_status()
        return response.json()
    except Exception as e:
        message = QCoreApplication.translate("updater",
                                             "Failed to check for latest release: {api_url} Error: {exception}").format(
            api_url=url, exception=e)
        qWarning(f"{_ID_TAG} {message}")
        return {}


def _find_latest_asset(data: dict, current_version) -> tuple:
    asset_regex = re.compile(r"([A-Za-z0-9._ -]+)[. _]v[. _](\d+)\.(\d+)\.(\d+)\.exe$", re.IGNORECASE)
    latest_asset = None
    latest_version = current_version

    for asset in data.get("assets", []):
        match = asset_regex.match(asset.get("name", ""))
        if match:
            found_version = ".".join(match.group(i) for i in range(2, 5))
            remote_version = version.parse(found_version)
            if remote_version > current_version:
                latest_asset = asset
                latest_version = remote_version

    return latest_asset, latest_version


def _download_and_verify_asset(asset: dict, display_name: str, out_path: str, title: str) -> bool:
    download_url = asset.get("browser_download_url", "")
    expected_digest = asset.get("digest", "")
    expected_size = asset.get("size", 0)

    if not download_url or not expected_digest:
        message = QCoreApplication.translate("updater", "Failed to get download URL or digest for latest release.")
        QMessageBox.critical(None, title, message)
        qCritical(f"{_ID_TAG} {message}")
        return False

    message = QCoreApplication.translate("updater",
                                         "Downloading latest version {display_name} from ({download_url})").format(
        display_name=display_name, download_url=download_url)
    qInfo(f"{_ID_TAG} {message}")

    try:
        with requests.get(download_url, timeout=10, stream=True) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))

            if total != expected_size:
                message = QCoreApplication.translate("updater",
                                                     "Unexpected file size. Expected {expected_size}, got {total}").format(
                    expected_digest=expected_digest, total=total)
                qWarning(f"{_ID_TAG} {message}")
                return False

            qDebug(f"{_ID_TAG} Size verified successfully: {total} bytes")

            progress = QProgressDialog("", "", 0, total)
            progress.setWindowTitle("Download")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setCancelButton(None)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            sha256 = hashlib.sha256()
            with open(out_path, "wb") as file, tqdm(total=total, unit="B", unit_scale=True, unit_divisor=1024,
                                                    desc=f"Downloading {display_name}") as bar:
                start_time = time.time()
                last_eta_update = 0
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    QApplication.processEvents()
                    if chunk:
                        file.write(chunk)
                        sha256.update(chunk)
                        downloaded += len(chunk)
                        progress.setValue(downloaded)
                        bar.update(len(chunk))

                        now = time.time()
                        elapsed = now - start_time
                        if elapsed > 0 and now - last_eta_update > 0.5:
                            speed = downloaded / elapsed / 1024 / 1024  # MB/s
                            eta = int((total - downloaded) / (downloaded / elapsed)) if downloaded > 0 else 0
                            message = QCoreApplication.translate("updater",
                                                                 "Downloading latest version {display_name} to ({out_path})\nETA: {eta}s - Speed: {speed:.1f} MB/s").format(
                                display_name=display_name, out_path=out_path, eta=_format_eta(eta), speed=speed)
                            progress.setLabelText(message)
                            last_eta_update = now

            progress.setValue(total)
            actual_digest = "sha256:" + sha256.hexdigest()
            if actual_digest != expected_digest:
                message = QCoreApplication.translate("updater",
                                                     "SHA256 mismatch! Expected: {expected_digest}, Got: {actual_digest}").format(
                    expected_digest=expected_digest, actual_digest=actual_digest)
                qWarning(f"{_ID_TAG} {message}")
                return False

            qDebug(f"{_ID_TAG} SHA256 verified successfully: {actual_digest}")
            return True

    except Exception as e:
        message = QCoreApplication.translate("updater", "Failed to download latest version:\n{exception}").format(
            exception=e).replace("\n", " ").strip()
        QMessageBox.critical(None, title, message)
        qCritical(f"{_ID_TAG} {message}")
        return False


def download_latest_exe_if_exist() -> None:
    api_url = f"https://api.github.com/repos/{GITHUB_REPO_NAME}/releases/latest"

    session = requests.Session()
    session.headers.update({
        "User-Agent": f"{APP_NAME}/{APP_VERSION} (+https://github.com/{GITHUB_REPO_NAME})",
        "Accept": "application/vnd.github+json"
    })

    data = _get_latest_release_data(session, api_url)
    if not data:
        return

    current_version = version.parse(APP_VERSION)
    latest_asset, latest_version = _find_latest_asset(data, current_version)

    if not latest_asset:
        message = QCoreApplication.translate("updater", "No new version found.")
        qInfo(f"{_ID_TAG} {message}")
        return

    close_splash_screen()

    title = QCoreApplication.translate("updater", "New Version Available")
    message = QCoreApplication.translate("updater",
                                         "A new version is available:\nCurrent version: {curr_ver}\nNew version: {latest_ver}\n\nDownload now?").format(
        curr_ver=APP_VERSION, latest_ver=latest_version.base_version)
    message_log = message.replace("\n", " ").replace("  ", " ").strip()
    qInfo(f"{_ID_TAG} {message_log}")

    if QMessageBox.information(None, title, message,
                               QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) != QMessageBox.StandardButton.Ok:
        message = QCoreApplication.translate("updater", "Download cancelled.")
        qInfo(f"{_ID_TAG} {message}")
        return

    display_name = f"{APP_NAME} v. {latest_version}.exe"
    out_path = QDir.toNativeSeparators(QDir(_get_desktop_path()).filePath(display_name))

    if QFileInfo.exists(out_path):
        _stop_and_run_new_exe(out_path)
        return

    exe_name = latest_asset.get("name", "")
    if not exe_name.lower().endswith(".exe") or any(x in exe_name for x in ["..", "/", "\\"]):
        message = QCoreApplication.translate("updater", "Invalid filename: {exe_name}").format(exe_name=exe_name)
        qWarning(f"{_ID_TAG} {message}")
        return

    if _download_and_verify_asset(latest_asset, display_name, out_path, title):
        message = QCoreApplication.translate("updater",
                                             "Downloading latest version {display_name} to ({out_path})").format(
            display_name=display_name, out_path=out_path)
        qInfo(f"{_ID_TAG} {message}")
        _stop_and_run_new_exe(out_path)
