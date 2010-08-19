This is a Python interface to Last.fm's acoustic fingerprinting library (called
`fplib`_) and its related API services. It currently supports fingerprint
matching (but not submission of new fingerprints), fingerprint ID lookup, and
track metadata lookup.

.. _fplib: http://github.com/lastfm/Fingerprinter


Installation
------------

To install, you will need `Cython`_ in addition to a compiler and the
dependencies required by fplib itself: `fftw`_ (single-precision) and
`libsamplerate`_. Once you have these, just type ``python setup.py install``
and you're good to go.

.. _Cython: http://cython.org/
.. _fftw: http://www.fftw.org/
.. _libsamplerate: http://www.mega-nerd.com/SRC/`


Running
-------

You can then run the included fingerprinter/lookup script, "lastmatch.py," to
test your installation::

    $ ./lastmatch.py my_great_music.mp3

The script outputs metadata matches from Last.fm's database. Note that, because
pylastfp does not decode MP3s, the script requires `pymad`_ to do this step.

.. _pymad: http://spacepants.org/src/pymad/


Using in Your Code
------------------

The script exhibits the usual way to use pylastfp, which is this::

    >>> import lastfp
    >>> ...`
    >>> matches = lastfp.match(apikey, path, pcmdata, samplerate, time_in_secs)
    >>> print matches[0]['artist'], '-', matches[0]['title']
    The National - Fake Emprire

Of course, you'll need some way to get a PCM stream from any audio you want to
fingerprint; this is (currently) outside the scope of this library. The
pcmdata parameter must be an iterable of Python ``buffer`` objects containing
PCM data as arrays of C ``short`` values.


To-Do
-----

Things to do:

- simple mechanism for loading PCM data (using pygst?)
- "full" fingerprint for submission
- silence-skipping optimization
- rate limiting for API calls
- error handling for API calls


Credits
-------

This library is by `Adrian Sampson`_. It includes the fplib source code, which
is by `Last.fm`_. fplib is licensed under the LGPLv3, so pylastfp uses the same
license.

.. _Adrian Sampson: mailto:adrian@radbox.org
.. _Last.fm: http://last.fm/
