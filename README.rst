This is a Python interface to Last.fm's acoustic fingerprinting library (called
`fplib`_) and its related API services. It performs fingerprint
matching, fingerprint ID lookup, and track metadata lookup. It also has some
helpers for decoding audio files.

.. _fplib: http://github.com/lastfm/Fingerprinter


Installation
------------

To install, you will a compiler and the dependencies required by fplib
itself: `fftw`_ (single-precision) and `libsamplerate`_. Once you have these,
just type ``python setup.py install`` in the source distribution and you're
good to go.

.. _fftw: http://www.fftw.org/
.. _libsamplerate: http://www.mega-nerd.com/SRC/`

Too build from the version control source (i.e., not from a released
distribution), you will also need `Cython`_. (The source distributions include
the generated C++ file, avoiding the need for Cython. This package's
``setup.py`` plays tricks to detect whether you have Cython installed.)

.. _Cython: http://cython.org/


Running
-------

You can then run the included fingerprinter/lookup script, "lastmatch.py," to
test your installation::

    $ ./lastmatch.py mysterious_music.mp3

The script outputs metadata matches from Last.fm's database. This script
uses `Gstreamer's Python bindings`_ to decode MP3s. You can also use `pymad`_
instead of Gstreamer (for MPEG audio only) by supplying the ``-m`` flag::

    $ ./lastmatch.py -m mysterious_music.mp3

.. _Gstreamer's Python bindings:
   http://gstreamer.freedesktop.org/modules/gst-python.html
.. _pymad: http://spacepants.org/src/pymad/


Using in Your Code
------------------

The script exhibits the usual way to use pylastfp, which is this::

    >>> import lastfp
    >>> xml = lastfp.gst_match(apikey, path)
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

    >>> xml = lastfp.match(apikey, pcmdata, samplerate, time_in_secs)

Of course, you'll need a PCM stream from any audio you want to
fingerprint. The pcmdata parameter must be an iterable of Python
``str`` or ``buffer`` objects containing PCM data as arrays of C ``short``
(16-bit integer) values.

The module internally performs thread-safe API limiting to 5 queries per
second, in accordance with `Last.fm's API TOS`_.

.. _Last.fm's API TOS: http://www.last.fm/api/tos


To-Do
-----

The fingerprinting library allows for an optimization that skips decoding
a few milliseconds at the beginning of every file. (See
``FingerprintExtractor::getToSkipMs()``, as demonstrated by the
`example client`_.) This will complicate the module's interface a bit because
the decoding source will need to know the amount of time to skip.

.. _example client:
    http://github.com/lastfm/Fingerprinter/blob/master/lastfmfpclient/
    src/main.cpp#L372

We should also probably detect and handle errors in calling the Last.fm API,
including both HTTP errors and the API's `error codes`_. Finally, the API
lets you submit existing metadata to help improve Last.fm's database;
we should allow this as an optional parameter.

.. _error codes: http://www.last.fm/api/errorcodes


Credits
-------

This library is by `Adrian Sampson`_. It includes the fplib source code, which
is by `Last.fm`_. fplib is licensed under the LGPLv3, so pylastfp uses the same
license.

.. _Adrian Sampson: mailto:adrian@radbox.org
.. _Last.fm: http://last.fm/
