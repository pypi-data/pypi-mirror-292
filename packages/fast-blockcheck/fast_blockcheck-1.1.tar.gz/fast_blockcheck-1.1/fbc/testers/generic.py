import datetime
from abc import abstractmethod
from typing import Collection

from fbc.format import format_time
from fbc.targets import TestingTechnique


class BlockTester:
    name: TestingTechnique
    def run_test(self, urls: Collection[str], timeout: int, shuffle: bool) -> int:
        """
        Run full test iteration
        :param urls: URLs to check
        :param timeout: request timeout
        :param shuffle: whether to shuffle urls
        :return: number of successfully (HTTP < 400) accessed entries
        """
        number_of_successful = 0

        urls = self.get_links(urls, shuffle)
        total_number = len(urls)

        start_time = format_time(datetime.datetime.now())
        print(f"{start_time}: starting test: {self.name}")

        for url in urls:
            r = self.test_url_availability(url, timeout)
            number_of_successful += int(r)

        print(f"{number_of_successful}/{total_number} domains loaded")
        return number_of_successful

    @abstractmethod
    def get_links(self, links: Collection[str], shuffle: bool) -> Collection[str]:
        """
        :param links: all possible links
        :param shuffle: randomise links order
        :return: only links suitable for current technique
        """
        pass

    @abstractmethod
    def test_url_availability(self, url: str, timeout: int) -> bool:
        """
        :return: URL is available
        """
        pass

    def report_url(self, url: str, timestamp: datetime.datetime, status_code: int | str):
        """Report test status for URL"""
        print(f"{format_time(timestamp)}: ({status_code}) {url}")