# etckeeper.py, support etckeeper for dnf
#
# Copyright (C) 2014 Peter Listiak
# https://github.com/plistiak/dnf-etckeeper
#
# Later modifications by Petr Spacek:
# Distutils code below was copied from etckeeper-bzr distributed with v1.15
#

import logging
import subprocess
import dnf

logger = logging.getLogger('dnf.plugin')


class Etckeeper(dnf.Plugin):

    name = 'etckeeper'

    def _run_command(self, command):
        logger.debug('Etckeeper plugin: %s', command)
        try:
            with open("/dev/null", "wb") as devnull:
                ret = subprocess.call(("etckeeper", command),
                                      stdout=devnull, stderr=devnull,
                                      close_fds=True)
                if ret > 0:
                    logger.warning('"etckeeper %s" failed (exit code %d)' % (command, ret))
                if ret < 0:
                    logger.warning('"etckeeper %s" died (signal %d)' % (command, -ret))
        except OSError as err:
            logger.warning('Failed to run "etckeeper %s": %s' % (command, err))

    def resolved(self):
        self._run_command("pre-install")

    def transaction(self):
        self._run_command("post-install")

if __name__ == "__main__":
    from distutils.core import setup
    setup(name="dnf-etckeeper",
          packages=["dnf-plugins"],
          package_dir={"dnf-plugins":"etckeeper-dnf"})
