import datetime
import random
import socket
from typing import Collection

from fbc.targets import TestingTechnique
from fbc.testers.generic import BlockTester
from fbc.utils.http3 import get_http3


class QUICTester(BlockTester):
    name = TestingTechnique.QUICProtocol

    def get_links(self, links: Collection[str], shuffle: bool) -> Collection[str]:
        # From https://bagder.github.io/HTTP3-test/
        urls = [
            "https://quic.nginx.org/test",
            "https://cloudflare-quic.com/",
            "https://quic.rocks:4433/",
            "https://quic.aiortc.org/",
            "https://f5quic.com:4433/",
            "https://pgjones.dev/",
            "https://quic.westus.cloudapp.azure.com/",
        ]
        if shuffle:
            random.shuffle(urls)
        return urls

    def test_url_availability(self, url: str, timeout: int) -> bool:
        try:
            response = get_http3(url, timeout)
            is_quic = response.http_version == 'HTTP/3'

            if is_quic:
                status = response.status_code
            else:
                status = "NON_QUIC"

            self.report_url(url, datetime.datetime.now(), status)
            return response.status_code < 400 and is_quic
        except (socket.gaierror, ConnectionError):
            self.report_url(url, datetime.datetime.now(), "ERR")
            return False

    # with httpx.Client(http1=False, http2=False) as client:
    #     response = client.get(url, timeout=timeout)
    #
    #     print(response.content)
    #     self.report_url(url, datetime.datetime.now(), response.status_code)
    #     return response.status_code < 400
