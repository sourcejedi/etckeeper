# etckeeper.py, support etckeeper for dnf
#
# Copyright (C) 2014 Peter Listiak
# https://github.com/plistiak/dnf-etckeeper
#
# Later modifications by Petr Spacek:
# Distutils code below was copied from etckeeper-bzr distributed with v1.15
#

from __future__ import unicode_literals
from dnfpluginscore import logger

import subprocess
import locale
import dnf


class Etckeeper(dnf.Plugin):

    name = 'etckeeper'

    def _debug(self, msg):
        logger.debug('Etckeeper plugin: %s', msg)

    def _log_pipe(self, pipe):
        # etckeeper & git messages should be encoded using the default locale
        # (or us-ascii, which is a strict subset).
        #
        # Normally py2 breaks if you print arbitrary unicode when stdout is
        # not a tty (UnicodeEncodeError).  However the dnf cli has a
        # workaround; it will survive regardless of what we do.
        #
        # Then we have logging.FileHandler.  In py3 it will use
        # locale.getpreferredencoding(False) by default.  This should match
        # the default locale, unless we are on py < 3.2, AND the program
        # forgot to call setlocale(LC_ALL, "").  dnf already calls
        # setlocale(LC_ALL, ""), so it will be nice and consistent.
        # In fact it is the dnf *library* that calls setlocale, this is not
        # really recommended, but it makes me pretty confident here.
        #
        # errors='replace' means that decode errors give us '\ufffd', which
        # causes UnicodeEncodeError in some character encodings.  Let us
        # simulate a round-trip through errors='replace', by replacing them
        # with a question mark.
        #
        # The story for py2 is more complex.  In libdnf 2.6.3, the logfile
        # is equivalent to hardcoding a utf8 encoding.  That is survivable
        # (and if it changes to match py3, it will also be fine).
        #
        encoding = locale.getpreferredencoding(False)
        for line in pipe:
            line = line.decode(encoding, 'replace')
            line.replace('\ufffd', '?')
            line = line.rstrip('\n')
            logger.info('%s', line)

    def resolved(self):
        self._debug('pre transaction commit')
        proc = subprocess.Popen(("etckeeper", "pre-install"),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                close_fds=True)
        self._log_pipe(proc.stdout)
        ret = proc.wait()
        if ret != 0:
            raise dnf.exceptions.Error('etckeeper returned %d' % ret)

    def transaction(self):
        self._debug('post transaction commit')
        proc = subprocess.Popen(("etckeeper", "post-install"),
                                stdout=None,
                                stderr=subprocess.PIPE,
                                close_fds=True)
        self._log_pipe(proc.stderr)
        ret = proc.wait()
        if ret != 0:
            logger.err('etckeeper returned %d' % ret)

if __name__ == "__main__":
    from distutils.core import setup
    setup(name="dnf-etckeeper",
          packages=["dnf-plugins"],
          package_dir={"dnf-plugins":"etckeeper-dnf"})
