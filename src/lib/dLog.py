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

import sys, os, time, datetime
sys.path.append("..")
sys.setdefaultencoding("utf-8")
from lib import Dshield

PROC_DIR =  os.path.abspath('..')
LOGS_DIR = PROC_DIR + '/logs/'

'''
#==================================
# 日志记录类型
#==================================
# [LOCK]     封锁
# [UNLOCK]   解封
# [ERROR]    错误消息
# [RECORD]   记录,不封锁
# [REBL]     重载封锁列表
# [MAIL]     发送邮件
#==================================
'''
def save_log(type, data):
	logdir = LOGS_DIR + time.strftime('%Y_%m', time.localtime()) + '/'
	
	if not os.path.exists(logdir):
		os.system('mkdir -p ' + logdir)
		os.chmod(logdir, 777)
	
	log_file = logdir + time.strftime('%Y_%m_%d', time.localtime()) + '_' + Dshield().avr['logFile']
	f = open(log_file, 'a')
	f.write('['+type+'] ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(data) + '\n')
	f.close()
