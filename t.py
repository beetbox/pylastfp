import fplib
import mad
import sys
import urllib
import urllib2

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
    for (key, value) in fields:
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

f = mad.MadFile(sys.argv[1])
fpdata = fplib.fingerprint(readf(f), f.samplerate(), 2)
print urllib.quote(fpdata)

url = 'http://www.last.fm/fingerprint/query/'
params = {
    
}
