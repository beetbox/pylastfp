#!/usr/bin/env python

import mad
import sys
import os
import lastfp

BLOCK_SIZE = 1024
def readblocks(f):
    while True:
        out = f.read(BLOCK_SIZE)
        if not out:
            break
        yield out

if __name__ == '__main__':
    path = os.path.abspath(sys.argv[1])
    f = mad.MadFile(path)
    matches = lastfp.match(path, readblocks(f), f.samplerate(), f.total_time())
    for track in matches:
        print '%s - %s' % (track['artist'], track['title'])
