import time

from fbc.testers.generic import BlockTester
from fbc.targets import TestingTechnique
from fbc.testers.basic_domain import BasicDomainTester
from fbc.testers.quic import QUICTester


def get_tester(technique: TestingTechnique) -> BlockTester:
    """
    :param technique: Testing technique name
    :raises TypeError: specified technique is not supported yet
    :return: Tester object
    """
    if technique == TestingTechnique.BasicDomain:
        return BasicDomainTester()
    if technique == TestingTechnique.QUICProtocol:
        return QUICTester()
    else:
        raise  TypeError(f"Unsupported testing technique: {technique}")


def fast_blockcheck(urls: list[str], timeout: int, shuffle: bool, repeat: int, technique: TestingTechnique):
    """
    Monitor URLs availability
    :param urls: URLs to test
    :param timeout: request timeout in seconds
    :param shuffle: whether to shuffle URLs each iteration
    :param repeat: repeat interval in minutes, 0 to run only once
    :param technique: testing method name
    """

    try:
        test_technique = get_tester(technique)
    except TypeError as e:
        print(e)
        exit(1)
    while True:
        test_technique.run_test(urls, timeout, shuffle)
        if not repeat:
            break
        else:
            print(f"Waiting for {repeat}min to repeat")
            time.sleep(60 * repeat)
