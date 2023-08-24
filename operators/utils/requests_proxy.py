# -*- coding:utf-8 -*-

# urllib3 and socks
from urllib3.contrib.socks import SOCKSProxyManager
import ssl
import urllib.request
import socket
import os
import sys
import subprocess
import bpy
from pathlib import Path
from ...prefs import BGIS_PREFS

PKG, SUBPKG = __package__.split('.', maxsplit=1)

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


class Response:
    
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

    def read(self):
        return self.r.data
        pass

    def close(self):
        pass

def getSocksProxy():
    output = subprocess.getoutput("scutil --proxy")
    socksEnable = False
    socksProxy = None
    socksPort = None
    for line in output.splitlines():
        found = line.find('SOCKSEnable')
        if found > 0:
            socksEnable = bool(line.split(':')[1].strip())
            continue
        found = line.find('SOCKSProxy')
        if found > 0:
            socksProxy = line.split(':')[1].strip()
            continue
        found = line.find('SOCKSPort')
        if found > 0:
            socksPort = int(line.split(':')[1].strip())
            continue
    if socksEnable:
        return (socksProxy, socksPort)
    return (None, None)

    
def urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
    prefs = bpy.context.preferences.addons[PKG].preferences
    socksProxy = None
    socksPort = None
    if prefs.socksProxyStrategy == 'M':
        socksProxy = prefs.socksProxy
        socksPort = int(prefs.socksPort)
    elif prefs.socksProxyStrategy == 'S':
        (socksProxy, socksPort) = getSocksProxy()
    
    # log.debug("Proxy: {} {} {}".format(prefs.socksProxyStrategy, socksProxy, socksPort))
    
    if not socksProxy or not socksPort:
        return urllib.request.urlopen(url, data, timeout)

    headers = None
    if isinstance(url, urllib.request.Request):
        request = url
        data = data or request.data
        url = request.full_url
        headers = request.headers

    
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