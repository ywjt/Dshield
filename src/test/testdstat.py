#!/usr/bin/env python
# encoding=utf-8

import sys
sys.path.append("..")
from lib.dStat import Dstat
from time import sleep

if __name__ == '__main__':
	while True:
		print Dstat().net()
		#sleep(1)
