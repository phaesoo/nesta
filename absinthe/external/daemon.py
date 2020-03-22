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
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr
        self._pidfile = pidfile

    def _daemonize(self):
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
        si = open(self._stdin, 'r')
        so = open(self._stdout, 'a+')
        se = open(self._stderr, 'a+')
        #os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def _remove_pidfile(self):
        os.remove(self._pidfile)

    def start(self):
        print ("start daemon")
        """
        start the daemon
        """
        # check for a pidfile to see if the daemon already runs
        try:
            pf = open(self._pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self._pidfile)
            sys.exit(1)

        # daemonize current process
        self._daemonize()

        # dump pidfile
        pid = str(os.getpid())
        open(self._pidfile, 'w+').write("%s\n" % pid)
        atexit.register(self._remove_pidfile)

        self._run()

    def stop(self):
        print ("stop daemon")
        """
        Stop the daemon
        """
        # get the pid from the pidfile

        if not os.path.exists(self._pidfile):
            message = "pidfile %s does not exist. Daemon is not running?\n"
            sys.stderr.write(message % self._pidfile)
            return
        
        with open(self._pidfile, 'r') as f:
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
    def _run(self):
        """
        should override this method when you subclass Daemon. it will be called after the process has been
        _daemonized by start() or restart().
        """
