import requests
from urllib.parse import urlparse

from bs4 import BeautifulSoup


def url_parse(url: str) -> str:
    parsed_url = urlparse(url)
    result = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return result


def extract_page_data(url):
    try:
        r = requests.get(url)
        status = r.status_code
        data = {}
        if status != 200:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        h1_tag = soup.find('h1')
        h1_text = h1_tag.text if h1_tag else ''
        title_tag = soup.find('title')
        title_text = title_tag.text if title_tag else ''
        description_tag = soup.find('meta',
                                    attrs={'name': 'description'})
        description_text = (description_tag['content']
                            if description_tag else '')
        data['h1'] = h1_text
        data['title'] = title_text
        data['description'] = description_text
        data['status'] = '200'
        return data
    except Exception:
        return
