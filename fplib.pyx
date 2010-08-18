cdef extern from "FingerprintExtractor.h":
    ctypedef struct StringSizePair "std::pair<const char*, size_t>":
        char *first
        unsigned int second
    ctypedef struct FingerprintExtractor "fingerprint::FingerprintExtractor":
        void initForQuery(int freq, int nchannels, int duration)
        void initForFullSubmit(int freq, int nchannels)
        bool process(short* pPCM, size_t num_samples,
                     bool end_of_stream)
        StringSizePair getFingerprint()
    FingerprintExtractor *newExtractor \
            "new fingerprint::FingerprintExtractor" ()
    void delExtractor "delete" (FingerprintExtractor *fe)

def testrun():
    cdef FingerprintExtractor *fe = newExtractor()
    fe.initForQuery(10, 2, -1)
    cdef StringSizePair out
    out = fe.getFingerprint()

    fplen = out.second
    if fplen == 0:
        # Fingerprinting failed.
        return None
    else:
        #fixme:
        # Copy the first fplen bytes from out.second and then return.
        return 5

def fingerprint(pcmiter, samplerate, channels, duration=-1):
    cdef FingerprintExtractor *fe = newExtractor()
    cdef char *bufcstr
    
    samplesize = sizeof(short)
    fe.initForQuery(samplerate, channels, duration)
    for buf in pcmiter:
        bufstr = str(buf)
        bufcstr = bufstr
        bufsize = len(buf)/samplesize
        print 'processing', repr(buf), bufsize
        res = fe.process(<short*>bufcstr, bufsize, False)
        print 'processed'
        if res:
            # Fingerprint ready.
            break
    else:
        # Extractor never became ready.
        return None
    # Success.
    return fe.getFingerprint().second
    # delExtractor(fe)
        
