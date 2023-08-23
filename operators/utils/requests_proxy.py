# -*- coding:utf-8 -*-

# urllib3 and socks
from urllib3.contrib.socks import SOCKSProxyManager
import ssl
import urllib.request
import socket
import os
import sys
import subprocess
from pathlib import Path

import logging
log = logging.getLogger(__name__)

try:
    import socks
except ImportError:    
    bin_folder = os.path.join(sys.prefix, 'bin')
    python_exe = os.path.join(bin_folder, os.listdir(bin_folder)[0])

    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    whl_path = os.path.join(source_dir, 'PySocks-1.7.1-py3-none-any.whl')
    subprocess.run([python_exe, "-m", "pip", "install", whl_path])

SOCKS_PROXY = "127.0.0.1"
SOCKS_PORT = 8119

class Response:
    def read(self):
        return self.r.data
        pass
    
    r = None

    @property
    def headers(self):
        return self.r.headers

    def __init__(self, response):
        self.r = response
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
    
def urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
    socksProxy = SOCKS_PROXY
    socksPort = SOCKS_PORT
    if not socksProxy or not socksPort:
        return urllib.request.urlopen(url, data, timeout)
    
    headers = None
    if isinstance(url, urllib.request.Request):
        request = url
        data = data or request.data
        url = request.full_url
        headers = request.headers

    log.debug("Proxy: {} {}".format(socksProxy, socksPort))

    
    proxy = SOCKSProxyManager('socks5h://{}:{}/'.format(socksProxy, socksPort), cert_reqs=ssl.CERT_NONE)
    if data:
        r = proxy.request('POST', url, data=data, headers=headers)
    else:
        r = proxy.request('GET', url, headers=headers)

    if not r:
        raise urllib.request.HTTPError(url, r.headers)
    if r.status != 200:
        raise urllib.request.HTTPError(url, r.status, r.reason, r.headers)
    
    return Response(r)

if __name__ == "__main__":
    url = "https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&west=119.02387890253334&east=119.24760547004699&south=30.181121842857074&north=30.2990178820855&outputFormat=GTiff&API_Key=a6fa47ae0f45eb354c81a95ac07a0325"
    rq = urllib.request.Request(url, headers={'User-Agent': "darwin"})
    print(urlopen(rq, timeout=120).read())
