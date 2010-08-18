import fplib
import mad
import sys
import urllib
import urllib2
import os
import hashlib

def readf(f):
    while True:
        out = f.read(100)
        if not out:
            break
        yield out


# http://code.activestate.com/recipes/146306/
def formdata_encode(fields):
    BOUNDARY = '----------form-data-boundary--_$'
    out = []
    for (key, value) in fields.items():
        out.append('--' + BOUNDARY)
        out.append('Content-Disposition: form-data; name="%s"' % key)
        out.append('')
        out.append(value)
    out.append('--' + BOUNDARY + '--')
    out.append('')
    body = '\r\n'.join(out)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body
def formdata_post(url, fields):
    content_type, data = formdata_encode(fields)
    req = urllib2.Request(url, data)
    req.add_header('Content-Type', content_type)
    return urllib2.urlopen(req).read()

path = os.path.abspath(sys.argv[1])
f = mad.MadFile(path)
fpdata = fplib.fingerprint(readf(f), f.samplerate(), 2)
# print urllib.quote(fpdata)

url = 'http://www.last.fm/fingerprint/query/'
params = {
    'artist': '',
    'album': '',
    'track': '',
    'duration': f.total_time()/1000,
    'filename': os.path.basename(path),
    'username': '',
    'sha256': hashlib.sha256(path).hexdigest(),
}
res = formdata_post('%s?%s' % (url, urllib.urlencode(params)),
                    {'fpdata': fpdata})
try:
    fpid, status = res.split()[:2]
    fpid = int(fpid)
except ValueError:
    print 'unparseable response:', res
if status == 'NEW':
    print 'new fingerprint:', fpid
elif status == 'FOUND':
    print 'fingerprint found:', fpid
    
    # Onward!
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'track.getFingerprintMetadata',
        'fingerprintid': fpid,
        'api_key': '2dc3914abf35f0d9c92d97d8f8e42b43',
    }
    out = urllib.urlopen('%s?%s' % (url, urllib.urlencode(params))).read()
    print out

else:
    print 'unknown status:', res

