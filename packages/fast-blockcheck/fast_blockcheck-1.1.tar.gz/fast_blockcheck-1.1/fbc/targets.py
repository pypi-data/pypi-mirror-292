import enum

default_urls = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://en.wikipedia.org",
    "https://www.github.com",
    "https://discord.com",
    "https://stackoverflow.com",

    "https://www.tiktok.com",

    "https://www.habr.com",
    "https://www.ya.ru",
    "https://www.gosuslugi.ru",
    "https://www.sberbank.ru",
    "https://vk.com",

    "https://web.telegram.org"
]

class TestingTechnique(enum.Enum):
    BasicDomain = 1
    IPOnly = 2
    ResolveDomainOnly = 3
    QUICProtocol = 4
def get_urls():
    return default_urls