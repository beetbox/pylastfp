This is a Python interface to Last.fm's acoustic fingerprinting library (called
`fplib`_) and its related API services. It performs fingerprint extraction,
fingerprint ID lookup, and track metadata lookup.

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

This library also depends on `audioread`_ to decode audio, although this
dependency is technically optional. If you already have a mechanism for decoding
audio files, there is no need to install audioread.

.. _audioread: https://github.com/sampsyo/audioread


Running
-------

You can run the included fingerprinter/lookup script, ``lastmatch.py``,
to test your installation::

    $ lastmatch.py mysterious_music.mp3

This will show metadata matches from Last.fm's database. The script uses
`audioread`_ to decode music, so it should transparently use a media library
available on your system (GStreamer, FFmpeg, MAD, or Core Audio on Mac OS X).


Using in Your Code
------------------

The script exhibits the usual way to use pylastfp, which is this::

    >>> import lastfp
    >>> xml = lastfp.match_file(apikey, path)
    >>> matches = lastfp.parse_metadata(xml)
    >>> print matches[0]['artist'], '-', matches[0]['title']
    The National - Fake Emprire

This example uses the ``match_file`` convenience function, which uses
`audioread`_ to decode audio data. The function imports the ``audioread`` module
when called, so if you don't want to depend on that, just don't call this
function.

If you have your own way of decoding audio, you can use the lower-level
interface::

    >>> xml = lastfp.match(apikey, pcmdata, samplerate, time_in_secs)

Of course, you'll need a PCM stream for the audio you want to
fingerprint. The pcmdata parameter must be an iterable of Python
``str`` or ``buffer`` objects containing PCM data as arrays of C ``short``
(16-bit integer) values.

Both functions (``match`` and ``match_file``) accept an additional optional
parameter called ``metadata``. It should be a dict containing your current guess
at the file's metadata. Last.fm might use this information to improve their
database. The dict should use these keys (all of which are optional):
``"artist"``, ``"album"``, and ``"track"``.

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

0.6
  Use `audioread`_ instead of the included `pygst`_ and `pymad`_ decoders.

0.5
  Handle empty responses from the API.
  ``setup.py`` now searches the `Homebrew`_ user-local prefix.

0.4
  Fix cleanup bug in gstdec that was causing files to remain open.

0.3
  Fix typo in handling of HTTP errors.
  Handle cases when HTTP status line is malformed.

0.2
  Fix a horrible memory leak.
  Fail safely when file is too short.
  Safely handle malformed XML returned from the API.
  Handle and expose HTTP failures.

0.1
  Initial release.

.. _Homebrew: http://mxcl.github.com/homebrew/
.. _pymad: http://spacepants.org/src/pymad/
.. _pygst: http://gstreamer.freedesktop.org/modules/gst-python.html


Credits
-------

This library is by `Adrian Sampson`_. It includes the fplib source code, which
is by `Last.fm`_. fplib is licensed under the LGPLv3, so pylastfp uses the same
license. pylastfp was written to be used with `beets`_, which you should
probably check out.

.. _Adrian Sampson: mailto:adrian@radbox.org
.. _Last.fm: http://last.fm/
.. _beets: http://beets.radbox.org/
