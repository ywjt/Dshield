#!/usr/bin/env python
# encoding=utf-8
"""
* @ Dshield for Python
##############################################################################
# Author: YWJT / Sunshine Koo                                                #
# Modify: 2016-12-08                                                         #
##############################################################################
# This program is distributed under the "Artistic License" Agreement         #
# The LICENSE file is located in the same directory as this program. Please  #
# read the LICENSE file before you make copies or distribute this program    #
##############################################################################
"""

import sys
sys.path.append("..")
import os, re, time
from time import sleep
from lib import Dshield


class Dstat(Dshield):

	def __init__(self):
		Dshield.__init__(self)
		
	def _read(self):
		fd = open("/proc/net/dev", "r")
		for line in fd.readlines():
			if line.find(self.avr['montInterface']) > 0:
				field = line.split(":")
				recv = field[1].split()[0]
				send = field[1].split()[8]
				continue
		fd.close()
		return (float(recv), float(send))
	  
	def net(self):
		net = {}
		(recv, send) = self._read()
		while True:  
			time.sleep(1)
			(new_recv, new_send) = self._read() 
			net['recv'] = "%.3f" %((new_recv - recv)/1024/1024)
			net['send'] = "%.3f" %((new_send - send)/1024/1024)
			return net

	def loadavg(self):
		loadavg = {}
		f = open("/proc/loadavg","r")
		con = f.read().split()
		f.close()
		loadavg['1m'] = con[0]
		loadavg['5m'] = con[1]
		loadavg['15m'] = con[2] 
		return loadavg







