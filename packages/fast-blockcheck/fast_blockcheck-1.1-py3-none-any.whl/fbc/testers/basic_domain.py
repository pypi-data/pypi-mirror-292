import datetime
import logging
import random
from typing import Iterable

import requests
import urllib3

from fbc.targets import TestingTechnique
from fbc.testers.generic import BlockTester

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger().setLevel(logging.DEBUG)


class BasicDomainTester(BlockTester):
    name = TestingTechnique.BasicDomain

    def test_url_availability(self, url: str, timeout: int = 5) -> bool:
        try:
            response = requests.get(url, timeout=timeout, verify=False)
            status_code = response.status_code
            success = response.ok

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            success = False

            if (isinstance(e.args[0], urllib3.exceptions.ReadTimeoutError) or
                    isinstance(e.args[0], requests.exceptions.ReadTimeout)):
                status_code = "TIME"
            else:
                # any other ConnectionError
                status_code = "ERR"
                logging.debug(e.args[0])
                logging.debug(type(e.args[0]))

        receive_time = datetime.datetime.now()
        self.report_url(url, receive_time, status_code)
        return success

    def get_links(self, links: Iterable[str], shuffle: bool):
        a = list(links)
        random.shuffle(a)
        return a
