"""
This file contains all code necessary for interfacing with XFOIL.

The Xfoil class circumvents blocking problems (caused by the interactive
nature of XFOIL) by using the NonBlockingStreamReader class, that runs the
blocking some_xfoil_subprocess.stdout.readline() call in a separate thread,
exchanging information with it using a queue.

This enables the Xfoil class to interact with XFOIL, and to read polars from
stdout instead of having to write a file to disk, eliminating latency there.
(Airfoil data still needs to be read from a file by XFOIL.)

Multiple XFOIL subprocesses can be run simultaneously, simply by constructing
the Xfoil class multiple times.

As such, this is probably the fastest and most versatile XFOIL automization
script out there. (I've seen a good MATLAB implementation, but it still relied
on files for output, and was not interactive.)
"""

from __future__ import division
import subprocess as subp
import numpy as np
import re

from threading import Thread
from Queue import Queue, Empty


def oper_alpha_visc(airfoil, alpha, Re, Mach=None,
                    normalize=True, plot=False, iterlim=None, gen_naca=False):
    """
    Convenience function that returns polar for specified airfoil and
    Reynolds number for (range of) alpha.
    Waits on XFOIL to finish so is blocking.
    
    args:
       airfoil        -> Airfoil file or NACA xxxx(x) if gen_naca flag set.
       alpha          -> Single value or list of [start, stop, interval].
       Re             -> Reynolds number

    kwargs:
       Mach           -> Mach number
       normalize=True -> Normalize airfoil through NORM command
       plot=False     -> Display XFOIL plotting window
       iterlim=None   -> Set a new iteration limit (XFOIL standard is 10)
       gen_naca=False -> Generate airfoil='NACA xxxx(x)' within XFOIL
    """

    xf = Xfoil()
    if normalize:
        xf.cmd("NORM")
    # Generate NACA or load from file
    if gen_naca:
        xf.cmd(airfoil)
    else:
        xf.cmd("LOAD " + airfoil)
    # Disable G(raphics) flag in Plotting options
    if not plot:
        xf.cmd("PLOP\nG\n\n", autonewline=False)
    # Enter OPER menu
    xf.cmd("OPER")
    if iterlim:
        xf.cmd("ITER {:.0f}".format(iterlim))
    xf.cmd("VISC {}".format(Re))
    if Mach:
        xf.cmd("MACH {:.3f}".format(Mach))
    # Turn polar accumulation on, double enter for no savefile or dumpfile
    xf.cmd("PACC\n\n\n", autonewline=False)
    # Try iterating over alpha
    try:
        if len(alpha) != 3:
            raise Warning("alpha is single value or [start, stop, interval]")
        # * unpacks, same as (alpha[0], alpha[1],...)
        xf.cmd("ASEQ {:.3f} {:.3f} {:.3f}".format(*alpha))
    # If iterating doesn't work, try assuming it's a single digit
    except TypeError:
        xf.cmd("ALFA {:.3f}".format(alpha))

    # List polar and send recognizable end marker
    xf.cmd("PLIS\nENDD\n", autonewline=False)
    
    # Keep reading until end marker is encountered
    output = ['']
    while not re.search("ENDD", output[-1]):
        line = xf.readline()
        if line:
            output.append(line)
            #print type(output[-1])
    print parse_stdout_polar(output)
    xf.close()


def parse_stdout_polar(lines):
    """Converts polar 'PLIS' data to array"""    
    def clean_split(s): return re.split('\s+', s.replace('\r\n',''))[1:]

    # Find location of data from ---- divider
    for i, line in enumerate(lines):
        if re.match('\s*---', line):
            dividerIndex = i
    
    # What columns mean
    data_header = clean_split(lines[dividerIndex-1])

    # Clean info lines
    info = ''.join(lines[dividerIndex-4:dividerIndex-2])
    info = re.sub("[\r\n\s]","", info)
    # Parse info
    def p(s): return float(re.search(s, info).group(1))
    infodict = {
     'xtrf_top': p("xtrf=(\d+\.\d+)"),
     'xtrf_bottom': p("\(top\)(\d+\.\d+)\(bottom\)"),
     'Mach': p("Mach=(\d+\.\d+)"),
     'Ncrit': p("Ncrit=(\d+\.\d+)"),
     'Re': p("Re=(\d+\.\d+e\d+)")
    }

    # Extract, clean, convert to array
    datalines = lines[dividerIndex+1:-2]
    data_array = np.array(
    [clean_split(dataline) for dataline in datalines], dtype='float')
    return data_array, data_header, infodict


class Xfoil():
    """
    This class basically represents an XFOIL child process, and should
    therefore not implement any convenience functions, only direct actions
    on the XFOIL process.
    """
    
    def __init__(self):
        """Spawn xfoil child process"""
        self.xfinst = subp.Popen("xfoil",
                  stdin=subp.PIPE, stdout=subp.PIPE, stderr=subp.PIPE)
        self._stdoutnonblock = NonBlockingStreamReader(self.xfinst.stdout)
        self._stdin = self.xfinst.stdin
        self._stderr = self.xfinst.stderr

    def cmd(self, cmd, autonewline=True):
        """Give a command. Set newline=False for manual control with '\n'"""
        n = '\n' if autonewline else ''
        self.xfinst.stdin.write(cmd + n)

    def readline(self):
        """Read one line, returns None if empty"""
        return self._stdoutnonblock.readline()

    def close(self):
        #print "Xfoil: instance closed through .close()"
        self.xfinst.kill()
    def __enter__(self):
        """Gets called when entering 'with ... as ...' block"""
        return self
    def __exit__(self):
        """Gets called when exiting 'with ... as ...' block"""
        #print "Xfoil: instance closed through __exit__"
        self.xfinst.kill()
    def __del__(self):
        """Gets called when deleted with 'del ...' or garbage collected"""
        #print "Xfoil: instance closed through __del__ (e.g. garbage collection)"
        self.xfinst.kill()


class UnexpectedEndOfStream(Exception): pass

class NonBlockingStreamReader:
    """From http://eyalarubas.com/python-subproc-nonblock.html"""
 
    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''
        self._s = stream
        self._q = Queue()
        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''
            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    #print "NonBlockingStreamReader: End of stream"
                    # Make sure to terminate
                    return
                    #raise UnexpectedEndOfStream
        self._t = Thread(target = _populateQueue,
                args = (self._s, self._q))
        self._t.daemon = True
        # Start collecting lines from the stream
        self._t.start()

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                    timeout = timeout)
        except Empty:
            return None


oper_alpha_visc("NACA 2215", [0,5,1], 2E6, Mach=.6, gen_naca=True)
