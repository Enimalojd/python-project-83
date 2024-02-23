import re


regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validator(url):
    errors = {}
    if len(url) > 255:
        errors['url'] = 'URL первышает 255 символов'
    if (re.match(regex, url) is not None) is False:
        errors['url'] = 'Некорректный URL'
    if url[-1] == '.':
        errors['url'] = 'Некорректный URL'
    return errors
