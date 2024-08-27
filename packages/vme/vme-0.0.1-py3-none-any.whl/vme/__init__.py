__all__ = ['send']

import json
from urllib.request import Request, urlopen
import urllib.error
import base64
import time
from io import IOBase

URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s'


def send(key, msg):
    webhook = URL % key
    if isinstance(msg, IOBase):
        raise NotImplementedError('to be implemented')
    send_text(webhook, msg)


def send_text(url, msg):
    data = json.dumps({
        'msgtype': 'text',
        'text': {'content': msg}
        }).encode('utf-8')
    req = Request(url, data=data, headers={'Content-Type': 'application/json'})
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
