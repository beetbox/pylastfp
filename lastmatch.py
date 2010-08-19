#!/usr/bin/env python
"""A simple program for using pylastfp to fingerprint and look up
metadata for MP3 files. Usage:
    $ python lastmatch.py my_great_music.mp3
"""
import mad
import sys
import os
import lastfp

API_KEY = '2dc3914abf35f0d9c92d97d8f8e42b43'

def readblocks(f, block_size=1024):
    """A generator that, given a file-like object, reads blocks (of
    the given size) from the file and yields them until f.read()
    returns a "falsey" value.
    """
    while True:
        out = f.read(block_size)
        if not out:
            break
        yield out

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python lastmatch.py my_great_music.mp3"
        sys.exit(1)
    path = os.path.abspath(sys.argv[1])
    f = mad.MadFile(path)

    # Perform match.
    try:
        xml = lastfp.match(API_KEY,
                           path,
                           readblocks(f),
                           f.samplerate(),
                           f.total_time()/1000)
    except lastfp.ExtractionError:
        print 'fingerprinting failed!'
        sys.exit(1)
    except lastfp.QueryError:
        print 'could not match fingerprint!'
        sys.exit(1)

    # Show results.
    matches = lastfp.parse_metadata(xml)
    for track in matches:
        print '%f: %s - %s' % (track['rank'], track['artist'], track['title'])
