#!/usr/bin/env python

from thinkrf.devices import WSA4000
from thinkrf.config import TriggerSettings

import sys
import time
import math

from numpy import fft, linspace

import sys

from gui import MainPanel
from PySide import QtGui, QtCore

REFRESH = 0.05

def logpower(i, q):
    return 20 * math.log10(math.sqrt((i*i) + (q*q)))

class WSA4000Connection(object):

    def __init__(self, host):
        # connect to wsa
        self.dut = WSA4000()
        self.dut.connect(host)

        # setup test conditions
        self.dut.request_read_perm()
        self.dut.ifgain(0)
        self.dut.freq(2450e6)
        self.dut.gain('high')
        self.dut.fshift(0)
        self.dut.decimation(0)

    def read_powdata(self):
        # capture 1 packet
        self.dut.capture(1024, 1)

        # read until I get 1 data packet
        while not self.dut.eof():
            pkt = self.dut.read()

            if pkt.is_data_packet():
                break

        # seperate data into i and q
        cdata = []
        for t in pkt.data:
            cdata.append( complex(t[0], t[1]) )

        # compute the fft of the complex data
        cfft = fft.fft(cdata)
        cfft = fft.fftshift(cfft)

        # compute power
        powdata = []
        for t in cfft:
            powdata.append(logpower(t.real, t.imag))
        return powdata




conn = WSA4000Connection(sys.argv[1])
app = QtGui.QApplication(sys.argv)
ex = MainPanel(conn)
timer = QtCore.QTimer(ex)
timer.timeout.connect(ex.update_screen)
timer.start(REFRESH)
sys.exit(app.exec_())



