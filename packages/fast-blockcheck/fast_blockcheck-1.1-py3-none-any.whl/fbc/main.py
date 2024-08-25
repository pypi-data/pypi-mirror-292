import argparse

from fbc.fbc import fast_blockcheck
from fbc.targets import get_urls, TestingTechnique

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--timeout", type=int, default=5, help="request timeout in seconds (5 by default)")
parser.add_argument("-s", "--shuffle", action='store_true', help="shuffle domains each time")
parser.add_argument("-r", "--repeat", type=int, default=0, help="repeat each N minutes")
parser.add_argument("--basic", action='store_true', help="basic domain test (default)")
parser.add_argument("--dns", action='store_true', help="DNS test")
parser.add_argument("--ip", action='store_true', help="IP addresses test")
parser.add_argument("--quic", action='store_true', help="QUIC protocol test")

args = parser.parse_args()



def main():
    urls = get_urls()
    techniques =  []
    if args.basic:
        techniques.append(TestingTechnique.BasicDomain)
    if args.dns:
        techniques.append(TestingTechnique.ResolveDomainOnly)
    if args.ip:
        techniques.append(TestingTechnique.IPOnly)
    if args.quic:
        techniques.append(TestingTechnique.QUICProtocol)

    if not techniques:
        techniques.append(TestingTechnique.BasicDomain)
    try:
        for technique in techniques:
            fast_blockcheck(urls, args.timeout, args.shuffle, args.repeat, technique)
    except KeyboardInterrupt:
        exit(0)
