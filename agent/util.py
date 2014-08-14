import magic
import mimetypes
from lxml import html
import simplejson as json
from urlparse import urljoin
import requests
import urlparse

def guess_extension(r):
    mime = magic.from_buffer(r.content, mime=True)
    extension = mimetypes.guess_extension(mime)
    return extension
def test_for_meta_redirections(r):
    extension = guess_extension(r)
    if extension == '.html':
        html_tree = html.fromstring(r.text)
        attr = html_tree.xpath("//meta[translate(@http-equiv, 'REFSH', 'refsh') = 'refresh']/@content")
        if not attr:
            return False, None
        attr = attr[0]
        splited = attr.split(";")
        wait, text = splited[:2]
        if text.lower().startswith("url="):
            url = text[4:]
            if not url.startswith('http'):
                # Relative URL, adapt
                url = urljoin(r.url, url)
            return True, url
    else:
        return False, None

def json_request(url, payload, **kwargs):
    headers = {'Content-type': 'application/json'}
    data = json.dumps(payload)
    return requests.post(url, data=data, headers=headers, **kwargs)

def extract_domain(url):
    return urlparse.urlparse(url).netloc
