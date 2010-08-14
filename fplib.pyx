cdef extern from "FingerprintExtractor.h":
    ctypedef struct StringSizePair "std::pair<const char*, size_t>":
        char *first
        unsigned int second
    ctypedef struct FingerprintExtractor "fingerprint::FingerprintExtractor":
        void initForQuery(int freq, int nchannels, int duration = -1)
        void initForFullSubmit(int freq, int nchannels)
        bool process(short* pPCM, size_t num_samples,
                     bool end_of_stream = false)
        StringSizePair getFingerprint()
    FingerprintExtractor *newExtractor \
            "new fingerprint::FingerprintExtractor" ()
    void delExtractor "delete" (FingerprintExtractor *fe)

def testrun():
    cdef FingerprintExtractor *fe = newExtractor()
    fe.initForQuery(10, 2)
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
