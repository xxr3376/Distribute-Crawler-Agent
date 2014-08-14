import requests
import util

def basic_downloader(query, base_headers, timeout):
    s = requests.session()
    url = query['url']
    arguments = {
        "headers": base_headers,
        "timeout": timeout,
        "allow_redirects": True,
    }
    if query.get('need_login', False):
        resource_id = query['resource']
        pass
    redirect = True
    while redirect:
        r = s.get(url, **arguments)
        redirect, url = util.test_for_meta_redirections(r)
        r.raise_for_status()
    return r

downloader_config = {
    'basic': basic_downloader,
    'render': None,
}
