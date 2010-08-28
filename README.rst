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

    $ ./lastmatch.py mysterious_music.mp3

The script outputs metadata matches from Last.fm's database. This script
uses `Gstreamer's Python bindings`_ to decode MP3s. You can also use `pymad`_
instead of Gstreamer (for MPEG audio only) by supplying the ``-m`` flag::

    $ ./lastmatch.py -m mysterious_music.mp3

.. _Gstreamer's Python bindings: http://gstreamer.freedesktop.org/modules/gst-python.html
.. _pymad: http://spacepants.org/src/pymad/

Using in Your Code
------------------

The script exhibits the usual way to use pylastfp, which is this::

    >>> import lastfp
    >>> xml == lastfp.gst_match(apikey, path)
    >>> matches = lastfp.parse_metadata(xml)
    >>> print matches[0]['artist'], '-', matches[0]['title']
    The National - Fake Emprire

This example uses the ``gst_match`` convenience function, which uses Gstreamer
to decode audio data. This function imports the Gstreamer module when called,
so if you don't want to depend on Gstreamer, just don't call this function.
Another similar function called ``mad_match`` imports the pymad module and
uses MAD to decode instead of Gstreamer.

If you have your own way of decoding audio, you can use the lower-level
interface::

    >>> xml = lastfp.match(apikey, path, pcmdata, samplerate, time_in_secs)

Of course, you'll need some way to get a PCM stream from any audio you want to
fingerprint; this is (currently) outside the scope of this library. The
pcmdata parameter must be an iterable of Python ``str`` of ``buffer`` objects
containing PCM data as arrays of C ``short`` (16-bit integer) values.


To-Do
-----

Things to do:

- silence-skipping optimization
- rate limiting for API calls
- error handling for API calls
- submit track metadata along with fingerprint data


Credits
-------

This library is by `Adrian Sampson`_. It includes the fplib source code, which
is by `Last.fm`_. fplib is licensed under the LGPLv3, so pylastfp uses the same
license.

.. _Adrian Sampson: mailto:adrian@radbox.org
.. _Last.fm: http://last.fm/
