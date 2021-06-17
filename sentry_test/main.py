from typing import Any, Dict

import sentry_sdk
from .sentry_socks5_transport.transport import Socks5HttpTransport


def setup_sentry(socks_url: str) -> None:
    dsn = "<dsn>"
    options: Dict[str, Any] = {
        "dsn": dsn,
        "transport_queue_size": sentry_sdk.consts.DEFAULT_QUEUE_SIZE,
        "ca_certs": None,
        "integrations": [],
    }
    transport = Socks5HttpTransport(socks_url, options)
    options = {**options, "transport": transport}
    sentry_sdk.init(options)  # type: ignore


def main() -> None:
    SOCKS_URL = "socks5h://127.0.0.1:1080"
    setup_sentry(SOCKS_URL)

    print("set up done")
    f()


def f() -> None:
    g()


def g() -> None:
    division_by_zero = 100 / 0
    print(division_by_zero)
