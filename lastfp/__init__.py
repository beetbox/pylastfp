# This file is part of pylastfp.
# Copyright 2011, Adrian Sampson.
# 
# pylastfp is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# pylastfp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with pylastfp.  If not, see
# <http://www.gnu.org/licenses/>.

"""Convenient Pythonic interface to Last.fm's fingerprinting library,
fplib. The match() function performs the fingerprinting and queries the
Last.fm servers for matches in one fell swoop.
"""
from __future__ import with_statement # for Python 2.5
import urllib
import urllib2
import xml.etree.ElementTree as etree
from xml.parsers.expat import ExpatError
import threading
import time
import httplib
from . import _fplib

URL_FPID = 'http://www.last.fm/fingerprint/query/'
URL_METADATA = 'http://ws.audioscrobbler.com/2.0/'

class FingerprintError(Exception):
    """Base class for all exceptions raised by this module."""
    pass


# Rate limiting.
QUERY_WAIT_TIME = 0.2 # Five queries per second.
_last_query_time = 0.0
_query_lock = threading.Lock()
def _query_wrap(fun, *args, **kwargs):
    """Wait until at least QUERY_WAIT_TIME seconds have passed
    since the last invocation of this function, then call the given
    function with the given arguments.
    """
    with _query_lock:
        global _last_query_time
        since_last_query = time.time() - _last_query_time
        if since_last_query < QUERY_WAIT_TIME:
            time.sleep(QUERY_WAIT_TIME - since_last_query)
        _last_query_time = time.time()
        return fun(*args, **kwargs)


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
class CommunicationError(FingerprintError):
    # Raised when we can't communicate with the APIs.
    pass
def fpid_query(duration, fpdata, metadata=None):
    """Send fingerprint data to Last.fm to get the corresponding
    fingerprint ID, which can then be used to fetch metadata.
    duration is the length of the track in (integral) seconds.
    If metadata is provided, it is a dictionary with three optional
    fields reflecting the current metadata for the file: "artist",
    "album", and "title". These values are optional but might help
    improve the database. Returns the fpid, an integer, or raises a
    QueryError.
    """
    metadata = metadata or {}
    params = {
        'artist': metadata.get('artist', ''),
        'album': metadata.get('album', ''),
        'track': metadata.get('title', ''),
        'duration': duration,
    }
    url = '%s?%s' % (URL_FPID, urllib.urlencode(params))
    try:
        res = _query_wrap(formdata_post, url, {'fpdata': fpdata})
    except urllib2.HTTPError:
        raise CommunicationError('ID query failed')
    except httplib.BadStatusLine:
        raise CommunicationError('bad response in ID query')
    except IOError:
        raise CommunicationError('ID query failed')
    
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
    params = {
        'method': 'track.getFingerprintMetadata',
        'fingerprintid': fpid,
        'api_key': apikey,
    }
    url = '%s?%s' % (URL_METADATA, urllib.urlencode(params))
    try:
        fh = _query_wrap(urllib.urlopen, url)
    except urllib2.HTTPError:
        raise CommunicationError('metadata query failed')
    except httplib.BadStatusLine:
        raise CommunicationError('bad response in metadata query')
    except IOError:
        raise CommunicationError('metadata query failed')
    return fh.read()

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
        try:
            if extractor.process(cur_block, done):
                # Success!
                break
        except RuntimeError, exc:
            # Exception from fplib. Most likely the file is too short.
            raise ExtractionError(exc.args[0])

        # End of file but processor never became ready?
        if done:
            raise ExtractionError()

    # Get resulting fingerprint data.
    out = extractor.result()
    if out is None:
        raise ExtractionError()
    
    # Free extractor memory.
    extractor.free()
    
    return out


# Main inteface.

def match(apikey, pcmiter, samplerate, duration, channels=2, metadata=None):
    """Given a PCM data stream, perform fingerprinting and look up the
    metadata for the audio. pcmiter must be an iterable of blocks of
    PCM data (buffers). duration is the total length of the track in
    seconds (an integer). metadata may be a dictionary containing
    existing metadata for the file (optional keys: "artist", "album",
    and "title"). Returns a list of track info dictionaries
    describing the candidate metadata returned by Last.fm. Raises a
    subclass of FingerprintError if any step fails.
    """
    fpdata = extract(pcmiter, samplerate, channels)
    fpid = fpid_query(duration, fpdata, metadata)
    return metadata_query(fpid, apikey)

class APIError(FingerprintError):
    # Raised for errors returned by the API service.
    def __init__(self, code, message):
        super(APIError, self).__init__(message)
        self.code = code
        self.message = message
def parse_metadata(xml):
    """Given an XML document (string) returned from metadata_query(),
    parse the response into a list of track info dicts. May raise an
    APIError if the lookup fails.
    """
    try:
        root = etree.fromstring(xml)
    except (ExpatError, etree.ParseError):
        # The Last.fm API occasionally generates malformed XML when its
        # includes an illegal character (UTF8-legal but prohibited by
        # the XML standard).
        raise CommunicationError('malformed XML response')
    
    status = root.attrib['status']
    if status == 'failed':
        error = root.find('error')
        raise APIError(int(error.attrib['code']), error.text)
    
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


# Convenience functions using an audio decoder.

def match_file(apikey, path, metadata=None):
    """Uses the audioread library to decode an audio file and match it.
    """
    import audioread
    with audioread.audio_open(path) as f:
        return match(apikey, iter(f), f.samplerate, int(f.duration),
                     f.channels, metadata)

# For backwards compatibility. Earlier versions of this library embedded
# a GStreamer-based decoder; this one depends on an external library
# that is a superset of that decoder.
gst_match = match_file
mad_match = match_file
