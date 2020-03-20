import os
import sys
import time
import atexit
from abc import ABC, abstractmethod
from signal import SIGTERM


class Daemon(ABC):
    """
    A generic daemon class.
    usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        # do the UNIX double-fork magic, see Stevens' "Advanced
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
            # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def _remove_pidfile(self):
        os.remove(self.pidfile)

    def start(self, daemonize=True):
        """
        start the daemon
        """
        # check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # start the daemon
        if daemonize:
            self.daemonize()

        # dump pidfile
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)
        atexit.register(self._remove_pidfile)

        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # get the pid from the pidfile

        if not os.path.exists(self.pidfile):
            message = "pidfile %s does not exist. Daemon is not running?\n"
            sys.stderr.write(message % self.pidfile)
            return
        
        with open(self.pidfile, 'r') as f:
            pid = int(f.read().strip())

        self._remove_pidfile()
        try:
            os.kill(pid, SIGTERM)
        except OSError:
            pass

    def restart(self):
        """
        restart the daemon
        """
        self.stop()
        self.start()

    @abstractmethod
    def run(self):
        """
        should override this method when you subclass Daemon. it will be called after the process has been
        daemonized by start() or restart().
        """
