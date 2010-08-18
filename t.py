import fplib
import mad
import sys

def readf(f):
    while True:
        out = f.read(100)
        if not out:
            break
        yield out

f = mad.MadFile(sys.argv[1])
print fplib.fingerprint(readf(f), f.samplerate(), 2)
