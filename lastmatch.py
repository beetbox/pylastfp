#!/usr/bin/env python
"""A simple program for using pylastfp to fingerprint and look up
metadata for MP3 files. Usage:
    $ python lastmatch.py mysterious_music.mp3
"""
import sys
import os
import lastfp

# This API key is specifically for this script, lastmatch.py. If you
# use pylastfp in your project, you'll want to generate your own. It's
# easy and free!
# http://last.fm/api/account
API_KEY = '7821ee9bf9937b7f94af2abecced8ddd'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python lastmatch.py mysterious_music.mp3"
        sys.exit(1)
    path = os.path.abspath(os.path.expanduser(sys.argv[1]))

    # Perform match.
    try:
        xml = lastfp.gst_match(API_KEY, path)
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
