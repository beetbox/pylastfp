import fplib
import urllib
import urllib2
import hashlib
import xml.etree.ElementTree as etree
import os

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

def getfpid(path, duration, fpdata):
    url = 'http://www.last.fm/fingerprint/query/'
    params = {
        'artist': '',
        'album': '',
        'track': '',
        'duration': duration/1000,
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
        return

    if status == 'NEW':
        print 'new fingerprint:', fpid
        return
    elif status == 'FOUND':
        print 'fingerprint found:', fpid
        return fpid
    else:
        print 'unknown status:', res
        return

def getmetadataxml(fpid):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'track.getFingerprintMetadata',
        'fingerprintid': fpid,
        'api_key': '2dc3914abf35f0d9c92d97d8f8e42b43',
    }
    out = urllib.urlopen('%s?%s' % (url, urllib.urlencode(params))).read()
    return out

def parsemetadataxml(xml):
    root = etree.fromstring(xml)
    out = []
    for track in root.find('tracks').findall('track'):
        out.append({
            'rank': track.attrib['rank'],
            'artist': track.find('artist').find('name').text,
            'artist_mbid': track.find('artist').find('mbid').text,
            'title': track.find('name').text,
            'track_mbid': track.find('mbid').text,
        })
    return out

def match(path, pcmiter, samplerate, duration, channels=2):
    fpdata = fplib.fingerprint(pcmiter, samplerate, channels)
    if not fpdata: return None
    fpid = getfpid(path, duration, fpdata)
    if not fpid: return None
    xml = getmetadataxml(fpid)
    return parsemetadataxml(xml)

