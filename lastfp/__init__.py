"""Convenient Pythonic interface to Last.fm's fingerprinting library,
fplib. The match() function performs the fingerprinting and queries the
Last.fm servers for matches in one fell swoop.
"""
import urllib
import urllib2
import xml.etree.ElementTree as etree
import os
from . import _fplib

class FingerprintError(Exception):
    """Base class for all exceptions raised by this module."""
    pass

# The stdlib doesn't yet have a facility for multipart/form-data HTTP
# requests, so here's an implementation based on this recipe:
# http://code.activestate.com/recipes/146306/
def formdata_encode(fields):
    """Encode fields (a dict) as a multipart/form-data HTTP request
    payload. Returns a (content type, request body) pair.
    """
    BOUNDARY = '----form-data-boundary-ZmRkNzJkMjUtMjkyMC00'
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
    """Send an HTTP request with a multipart/form-data body for the
    given URL and return the data returned by the server.
    """
    content_type, data = formdata_encode(fields)
    req = urllib2.Request(url, data)
    req.add_header('Content-Type', content_type)
    return urllib2.urlopen(req).read()

class QueryError(FingerprintError):
    pass
class BadResponseError(QueryError):
    pass
class NotFoundError(QueryError):
    pass
def fpid_query(path, duration, fpdata):
    """Send fingerprint data to Last.fm to get the corresponding
    fingerprint ID, which can then be used to fetch metadata.
    duration is the length of the track in (integral) seconds.
    Returns the fpid, an integer or raises a QueryError.
    """
    url = 'http://www.last.fm/fingerprint/query/'
    params = {
        'artist': '', # fixme
        'album': '',
        'track': '',
        'duration': duration,
        'filename': os.path.basename(path),
    }
    res = formdata_post('%s?%s' % (url, urllib.urlencode(params)),
                        {'fpdata': fpdata})
    try:
        fpid, status = res.split()[:2]
        fpid = int(fpid)
    except ValueError:
        raise BadResponseError('malformed response: ' + res)

    if status == 'NEW':
        raise NotFoundError()
    elif status == 'FOUND':
        return fpid
    else:
        raise BadResponseError('unknown status: ' + res)

def metadata_query(fpid, apikey):
    """Queries the Last.fm servers for metadata about a given
    fingerprint ID (an integer). Returns the XML response (a string).
    """
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'track.getFingerprintMetadata',
        'fingerprintid': fpid,
        'api_key': apikey,
    }
    return urllib.urlopen('%s?%s' % (url, urllib.urlencode(params))).read()

def parse_metadata(xml):
    """Given an XML document (string) returned from metadata_query(),
    parse the response into a list of track info dicts.
    """
    root = etree.fromstring(xml)
    out = []
    for track in root.find('tracks').findall('track'):
        out.append({
            'rank': float(track.attrib['rank']),
            'artist': track.find('artist').find('name').text,
            'artist_mbid': track.find('artist').find('mbid').text,
            'title': track.find('name').text,
            'track_mbid': track.find('mbid').text,
        })
    return out

class ExtractionError(FingerprintError):
    pass
def extract(pcmiter, samplerate, channels, duration = -1):
    """Given a PCM data stream, extract fingerprint data from the
    audio. Returns a byte string of fingerprint data. Raises an
    ExtractionError if fingerprinting fails.
    """
    extractor = _fplib.Extractor(samplerate, channels, duration)

    # Get first block.
    try:
        next_block = pcmiter.next()
    except StopIteration:
        raise ExtractionError()

    # Get and process subsequent blocks.
    while True:
        # Shift over blocks.
        cur_block = next_block
        try:
            next_block = pcmiter.next()
        except StopIteration:
            next_block = None
        done = next_block is None

        # Process the block.
        if extractor.process(cur_block, done):
            # Success!
            break

        # End of file but processor never became ready?
        if done:
            raise ExtractionError()

    # Get resulting fingerprint data.
    out = extractor.result()
    if out is None:
        raise ExtractionError()
    return out

def match(apikey, path, pcmiter, samplerate, duration, channels=2):
    """Given a PCM data stream, perform fingerprinting and look up the
    metadata for the audio. pcmiter must be an iterable of blocks of
    PCM data (buffers). duration is the total length of the track in
    seconds (an integer). Returns a list of track info dictionaries
    describing the candidate metadata returned by Last.fm. Raises a
    subclass of FingerprintError if any step fails.
    """
    fpdata = extract(pcmiter, samplerate, channels)
    fpid = fpid_query(path, duration, fpdata)
    return metadata_query(fpid, apikey)

def gst_match(apikey, path):
    """Uses Gstreamer to decode an audio file and perform a match.
    Requires the Python Gstreamer bindings.
    """
    from . import gstdec
    with gstdec.GstAudioFile(path) as f:
        return match(apikey, path, f, f.samplerate, 172, f.channels)
