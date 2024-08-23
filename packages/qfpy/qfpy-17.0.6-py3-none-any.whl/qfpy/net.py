"""
CLASH_PROXY

CLASH_PROXY_DICT

def cookies2dict(cookie_str: str) -> dict

def get_url_last_path(url: str) -> str
"""
from pathlib import Path
from urllib.parse import urlparse

# httpx 用字符串
CLASH_PROXY = "http://127.0.0.1:7890"
# requests 用字典
CLASH_PROXY_DICT = {
    "http": CLASH_PROXY,
    "https": CLASH_PROXY,
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"


def cookies2dict(cookies: str) -> dict:
    """
    把 cookies 字符串转换为字典

    cookie_str: str

    return: dict

    例如

    auth_token=824f3b553233b3f95436414e38d68e2c8a2380e7; ct0=6d9a80641d43b17852fda03513f200d2b3be76cba4c5b210326eb1689854553ddfa878424fe7517462a619268a9489a08a961c41e006722e0077f9bb2cc20830b943e50c4fabbf3158b42de5221c3f07

    ↓

    {'auth_token': '824f3b553233b3f95436414e38d68e2c8a2380e7', 'ct0': '6d9a80641d43b17852fda03513f200d2b3be76cba4c5b210326eb1689854553ddfa878424fe7517462a619268a9489a08a961c41e006722e0077f9bb2cc20830b943e50c4fabbf3158b42de5221c3f07'}
    """
    cookies_dict = {}
    for cookie in cookies.split(";"):
        key, value = cookie.strip().split("=", 1)
        cookies_dict[key] = value
    return cookies_dict


def get_url_last_path(url: str) -> str:
    """
    描述：获取 url 的最后一个 path

    示例：
    https://weibo.com/u/5288663041?tabtype=album → 5288663041
    """
    path = urlparse(url).path
    return Path(path).name


if __name__ == "__main__":
    print(get_url_last_path("https://weibo.com/u/5288663041"))