import time

import requests
from PySide6.QtCore import qDebug, QCoreApplication, qWarning

_ID_TAG = "[NETWORK_UTILS]"

_session = requests.Session()


def check_connection_quality(max_latency_ms: int = 350) -> bool:
    url = "https://www.google.com/generate_204"

    try:
        start = time.time()
        response = _session.get(url, timeout=5, allow_redirects=False, verify=True)
        response.raise_for_status()
        latency = (time.time() - start) * 1000  # ms

        if response.status_code == 204 and latency <= max_latency_ms:
            qDebug(f"{_ID_TAG} Connection quality is good: {int(latency)} ms")
            return True
        else:
            message = QCoreApplication.translate("network_utils",
                                                 "Connection quality is bad, unable to check new version: {latency} ms").format(
                latency=int(latency))
            qWarning(f"{_ID_TAG} {message}")
            return False
    except Exception as e:
        message = QCoreApplication.translate("network_utils",
                                             "Failed to check connection quality, unable to check new version: {exception}").format(
            exception=e)
        qWarning(f"{_ID_TAG} {message}")
        return False
