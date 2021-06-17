from __future__ import print_function

import io
import urllib3  # type: ignore
import certifi
import gzip

from datetime import datetime, timedelta

from sentry_sdk.utils import Dsn, logger, capture_internal_exceptions, json_dumps
from sentry_sdk.worker import BackgroundWorker
from sentry_sdk.envelope import Envelope

from sentry_sdk._types import MYPY

from sentry_sdk.transport import HttpTransport, Transport

if MYPY:
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import Iterable
    from typing import Optional
    from typing import Tuple
    from typing import Type
    from typing import Union

    from urllib3.poolmanager import PoolManager  # type: ignore
    from urllib3.poolmanager import ProxyManager

    from sentry_sdk._types import Event, EndpointType

    DataCategory = Optional[str]

try:
    from urllib.request import getproxies
except ImportError:
    from urllib import getproxies  # type: ignore


class Socks5HttpTransport(HttpTransport):
    """The SOCKS5-proxied HTTP transport."""

    def __init__(
        self,
        socks_url: str,
        options,  # type: Dict[str, Any]
    ):
        # type: (...) -> None
        from sentry_sdk.consts import VERSION

        Transport.__init__(self, options)
        assert self.parsed_dsn is not None
        self.options = options
        self._worker = BackgroundWorker(queue_size=options["transport_queue_size"])
        self._auth = self.parsed_dsn.to_auth("sentry.python/%s" % VERSION)
        self._disabled_until = {}  # type: Dict[DataCategory, datetime]
        self._retry = urllib3.util.Retry()

        assert "http_proxy" not in options
        assert "https_proxy" not in options
        self._pool = self._make_pool(
            self.parsed_dsn,
            socks_url=socks_url,
            ca_certs=options["ca_certs"],
        )

        from sentry_sdk import Hub

        self.hub_cls = Hub

    def _make_pool(
        self,
        parsed_dsn,  # type: Dsn
        socks_url,  # type: str
        ca_certs,  # type: Optional[Any]
    ):
        # type: (...) -> Union[PoolManager, ProxyManager]
        opts = self._get_pool_options(ca_certs)

        from urllib3.contrib.socks import SOCKSProxyManager
        return SOCKSProxyManager(socks_url, **opts)
