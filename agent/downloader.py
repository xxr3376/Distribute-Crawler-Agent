import requests

def basic_downloader(query, base_headers, timeout):
    url = query['url']
    arguments = {
        "headers": base_headers,
        "timeout": timeout,
        "allow_redirects": True,
    }
    if query.get('need_login', False):
        resource_id = query['resource']
        pass
    r = requests.get(url, **arguments)
    r.raise_for_status()
    return r

downloader_config = {
    'basic': basic_downloader,
    'render': None,
}
