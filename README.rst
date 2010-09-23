This is a Python interface to Last.fm's acoustic fingerprinting library (called
`fplib`_) and its related API services. It performs fingerprint extraction,
fingerprint ID lookup, and track metadata lookup. It also comes with some
helpers for decoding audio files.

.. _fplib: http://github.com/lastfm/Fingerprinter


Installation
------------

To install, you will need a compiler and the dependencies required by fplib
itself: `fftw`_ (compiled for single-precision floats) and `libsamplerate`_.
(On Debian/Ubuntu, the packages are ``libfftw3-dev`` and
``libsamplerate0-dev``.)

Once you have these, you can easily install from PyPI using `pip`_::

    $ pip install pylastfp

Or, if you don't have pip (or easy_install), head to the `download page`_.
The normal install command should work::

    $ python setup.py install
    
To build from the version control source (i.e., not from a release
tarball), you will also need `Cython`_. (The source distributions include
the generated C++ file, avoiding the need for Cython. This package's
``setup.py`` plays tricks to detect whether you have Cython installed.)

.. _fftw: http://www.fftw.org/
.. _libsamplerate: http://www.mega-nerd.com/SRC/
.. _Cython: http://cython.org/
.. _pip: http://pip.openplans.org/
.. _download page: http://github.com/sampsyo/pylastfp/downloads


Running
-------

You can run the included fingerprinter/lookup script, ``lastmatch.py``,
to test your installation::

    $ lastmatch.py mysterious_music.mp3

This will show metadata matches from Last.fm's database. The script
uses `Gstreamer's Python bindings`_ to decode MP3s. You can also use `pymad`_
instead of Gstreamer (for MPEG audio only) by supplying the ``-m`` flag::

    $ lastmatch.py -m mysterious_music.mp3

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
to decode audio data. The function imports the Gstreamer module when called,
so if you don't want to depend on Gstreamer, just don't call this function.
Another similar function called ``mad_match`` instead imports the pymad
library and uses MAD to decode instead of Gstreamer.

If you have your own way of decoding audio, you can use the lower-level
interface::

    >>> xml = lastfp.match(apikey, pcmdata, samplerate, time_in_secs)

Of course, you'll need a PCM stream for the audio you want to
fingerprint. The pcmdata parameter must be an iterable of Python
``str`` or ``buffer`` objects containing PCM data as arrays of C ``short``
(16-bit integer) values.

All of these functions (``match``, ``gst_match``, and ``mad_match``) accept
an additional optional parameter called ``metadata``. It should be a dict
containing your current guess at the file's metadata. Last.fm might use
this information to improve their database. The dict should use these keys
(all of which are optional): ``"artist"``, ``"album"``, and ``"track"``.

The module internally performs thread-safe API limiting to 5 queries per
second, in accordance with `Last.fm's API TOS`_.

.. _Last.fm's API TOS: http://www.last.fm/api/tos


To-Do
-----

The fingerprinting library allows for an optimization that skips decoding
a few milliseconds at the beginning of every file. (See
``FingerprintExtractor::getToSkipMs()``, as demonstrated by the
`example client`_.) Taking advantage of this will complicate the module's
interface a bit because the decoding source will need to know the amount of
time to skip.

.. _example client:
    http://github.com/lastfm/Fingerprinter/blob/master/lastfmfpclient/
    src/main.cpp#L372


Version History
---------------

0.2
  Fix a horrible memory leak.
  Fail safely when file is too short.
  Safely handle malformed XML returned from the API.

0.1
  Initial release.


Credits
-------

This library is by `Adrian Sampson`_. It includes the fplib source code, which
is by `Last.fm`_. fplib is licensed under the LGPLv3, so pylastfp uses the same
license. pylastfp was written to be used with `beets`_, which you should
probably check out.

.. _Adrian Sampson: mailto:adrian@radbox.org
.. _Last.fm: http://last.fm/
.. _beets: http://beets.radbox.org/
