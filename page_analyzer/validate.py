def validator(url):
    errors = {}
    if len(url) > 255:
        errors['url'] = 'URL is too long'
    return errors
