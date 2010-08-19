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

cdef class Extractor(object):
    """A task for fingerprinting a single audio file."""
    cdef FingerprintExtractor *fe
    def __init__(self, samplerate, channels, duration):
        """Start a new extraction task for a stream with the given
        parameters.
        """
        self.fe = newExtractor()
        self.fe.initForQuery(samplerate, channels, duration)
    def __del__(self):
        delExtractor(self.fe)

    def process(self, pcmblock, done):
        """Send a block of PCM data (as an array of C short integers)
        to the extractor. done is a boolean indicating whether this is
        the last block in the stream. Returns a boolean indicating
        whether the fingerprint is ready. If it returns True, call
        result() to get the output.
        """
        cdef char *bufcstr
        bufstr = str(pcmblock)
        bufsize = len(pcmblock)/sizeof(short)
        bufcstr = bufstr
        out = self.fe.process(<short*>bufcstr, bufsize, 0)
        return bool(out)
    
    def result(self):
        """Returns the result of a fingerprinting operation as a
        byte string. Only call this after process() returns True.
        Returns None if fingerprinting failed.
        """
        cdef StringSizePair outpair = self.fe.getFingerprint()
        if outpair.second:
            # Success.
            return outpair.first[:outpair.second]
        else:
            # Failure.
            return None
