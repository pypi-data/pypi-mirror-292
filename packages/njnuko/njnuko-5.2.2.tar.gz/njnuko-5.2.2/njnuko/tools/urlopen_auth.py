#!/usr/bin/env python
import urllib
import urllib.request


LOGIN = 'wesley'
PASSWD = "you'llNeverGuess"
URL = 'http://localhost'
REALM = 'Secure Archive'


def handler_version(url):
    from urllib import parse as urlparse
    hdlr = urllib.request.HTTPBasicAuthHandler()
    hdlr.add_password(REALM,urllib.parse.urlparse(url)[1],LOGIN,PASSWD)
    opener = urllib.request.build_opener(hdlr)
    urllib.request.install_opener(opener)
    return url

def request_version(url):
    from base64 import encodestring
    req = urllib.request.Request(url)
    b64str = encodestring('%s:%s' % (LOGIN,PASSWD))[:-1]
    req.add_header("Authorization","Basic %s" % b64str)
    return req

for funcType in ('handler','request'):
    print('*** Using %s:' % funcType.upper())
    url = eval('%s_version' % funcType)(URL)
    f = urllib.request.urlopen(url)
    print(f.readline())
    f.close()
