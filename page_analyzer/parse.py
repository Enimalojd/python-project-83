from urllib.parse import urlparse


def url_parse(url: str) -> str:
    parsed_url = urlparse(url)
    result = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return result