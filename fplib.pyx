"""Simple bindings for Last.fm's fingerprinting library, fplib."""

cdef extern from "FingerprintExtractor.h":
    ctypedef struct StringSizePair "std::pair<const char*, size_t>":
        char *first
        unsigned int second
    ctypedef struct FingerprintExtractor "fingerprint::FingerprintExtractor":
        void initForQuery(int freq, int nchannels, int duration)
        void initForFullSubmit(int freq, int nchannels)
        int process(short* pPCM, size_t num_samples,
                     int end_of_stream)
        StringSizePair getFingerprint()
    FingerprintExtractor *newExtractor \
            "new fingerprint::FingerprintExtractor" ()
    void delExtractor "delete" (FingerprintExtractor *fe)

def fingerprint(pcmiter, samplerate, channels, duration=-1):
    """Performs a fingerprint extraction for the PCM stream provided.
    pcmiter must be an iterable of buffer objects containing short
    integers for the PCM audio data. samplerate, channels, and
    duration all describe the stream's parameters. Returns a byte
    string of raw fingerprint data when successful and None when
    unsuccessful.
    """
    cdef FingerprintExtractor *fe = newExtractor()
    cdef char *bufcstr
    cdef StringSizePair outpair
    
    samplesize = sizeof(short)
    fe.initForQuery(samplerate, channels, duration)
    for buf in pcmiter:
        bufstr = str(buf)
        bufcstr = bufstr
        bufsize = len(buf)/samplesize
        res = fe.process(<short*>bufcstr, bufsize, 0)
        if res:
            # Fingerprint ready.
            break
    else:
        # Extractor never became ready.
        return None

    outpair = fe.getFingerprint()
    if outpair.second:
        # Success.
        out = outpair.first[:outpair.second]
    else:
        # Failure.
        out = None
    delExtractor(fe)
    return out
