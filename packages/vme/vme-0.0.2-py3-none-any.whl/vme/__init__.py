__all__ = ['send', 'send_file']

import json
from urllib.request import Request, urlopen
import urllib.error
import base64
import hashlib
import time
from io import IOBase


URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s'
JPG = b'\xFF\xD8\xFF'
PNG = b'\x89\x50\x4E\x47'


def send(key, msg):
    if isinstance(msg, str):
        send_text(URL % key, msg)
        return
    if not isinstance(msg, bytes):
        raise TypeError(f'only string or binary data allowed ({type(msg)})')

    text = None
    try:
        text = msg.decode('utf-8')
    except UnicodeDecodeError:
        pass
    if text:
        send(key, text)
    elif msg.startswith(JPG) or msg.startswith(PNG):
        send_image(URL % key, msg)
    else:
        raise ValueError(f'not text nor PNG/JPG image')


def send_text(url, msg):
    json_request(url, {
        'msgtype': 'text',
        'text': {'content': msg}
        })


def send_image(url, data):
    json_request(url, {
        'msgtype': 'image',
        'image': {
            'md5': hashlib.md5(data).hexdigest(),
            'base64': base64.b64encode(data).decode('ascii')
        }
    })


def send_file(key, fname):
    raise NotImplementedError('file sending not implemented yet')


def json_request(url, data):
    msg = json.dumps(data).encode('utf-8')
    req = Request(url, data=msg, headers={'Content-Type': 'application/json'})
    reply = robust_request(req)
    if reply['errcode']:
        raise RuntimeError(reply.get('errmsg', ''))


def robust_request(req, timeout=5, retries=3, delay=1):
    err = None
    for i in range(retries):
        try:
            with urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            if i + 1 >= retries:
                err = str(e)
                break
            time.sleep(delay)
    raise RuntimeError(err)

### vme/__init__.py ends here
