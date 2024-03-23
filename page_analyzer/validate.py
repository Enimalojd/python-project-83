import validators


def valid_url(url):
    errors = {}
    if not validators.url(url):
        errors['url'] = 'Некорректный URL'
    if len(url) > 255:
        errors['url'] = 'URL первышает 255 символов'
    return errors
