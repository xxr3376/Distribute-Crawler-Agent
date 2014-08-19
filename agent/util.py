import magic
import mimetypes
from lxml import html, etree
import simplejson as json
from urlparse import urljoin
import requests
import urlparse
from bs4 import UnicodeDammit

def guess_extension(r):
    mime = ''
    try:
        mime = r.headers['Content-Type'].split(';')[0].strip()
        if len(mime) <= 0:
            raise Exception('No Mine')
    except:
        mime = magic.from_buffer(r.content, mime=True)

    extension = mimetypes.guess_extension(mime)
    return extension

def guess_encoding(r, extension):
    need_guess = False
    try:
        encode = r.headers['Content-Type'].split(';')[1].strip()
        encode = encode.lstrip('charset=')
        if len(encode) <= 0:
            raise Exception('No Charset')
    except:
        need_guess = True
    if need_guess:
        converted = UnicodeDammit(r.content, is_html=(extension=='.html'))
        if not converted.unicode_markup:
            print 'Failed to detect encoding, tried [%s]' % ', '.join(converted.triedEncodings)
            return None
        encode = converted.original_encoding
    return encode

def test_for_meta_redirections(r):
    extension = guess_extension(r)
    if extension == '.html':
        html_tree = html.fromstring(r.text)
        attr = html_tree.xpath("//*[not(self::noscript)]/meta[translate(@http-equiv, 'REFSH', 'refsh') = 'refresh']/@content")
        if not attr:
            return False, None
        attr = attr[0]
        splited = attr.split(";")

        # len < 2 means this ask for refresh itself
        if len(splited) < 2:
            return False, None

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


from functools import update_wrapper
def retry(times, except_callback=None, fatal_callback=None):
    def decorator(func):
        def wraper_func(*args, **kw):
            error_count = 0
            while True:
                try:
                    result = func(*args, **kw)
                    break
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as e:
                    if except_callback:
                        except_callback(e, *args)
                    error_count += 1
                    if error_count >= times:
                        if fatal_callback:
                            result = fatal_callback(e, *args)
                        else:
                            result = None
                        break
            return result
        return update_wrapper(wraper_func, func)
    return decorator
