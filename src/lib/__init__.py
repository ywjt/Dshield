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

import sys, os
reload(sys)
sys.path.append("..")
import commands
import datetime, time
from time import sleep
from lib.loadConf import LoadConfig
import functools
import threading

def async(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		my_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
		my_thread.start()
	return wrapper


class Dshield(object):
	avr = {}
	avr['version'] = '4.0.0' #当前版本
	avr['logFile'] = 'running.log' #日志文件
	avr['maximumAllowedConnectionsPerIP'] = 200 #最大ip连接数
	avr['maximumAllowedConnectionsPerTTL'] = 100000 #最大ttl连接数
	avr['adminEmail'] = '' #管理员邮箱
	avr['whitelistIPs'] = {} #白名单
	avr['blockTime'] = '1h' #封锁时间
	avr['blockedIPs'] = {}  #黑名单
	avr['exectime'] = 1     #检测间隔
	avr['montport'] = '*'   #监控端口
	avr['montInterface'] = '' #网络接口
	avr['montlisten'] = False #监听模式
	avr['montProtocol'] = '' #监听协议
	avr['sender'] = ''     #发送者
	avr['receiver'] = []   #收接人列表
	avr['smtpserver'] = '' #SMTP服务器
	avr['username'] = ''   #用户名
	avr['password'] = ''   #验证密码
	avr['type'] = ''       #发信模式,默认不使用ssl
	keepRunning = True


	def __init__(self):
		self.avr['logFile'] = LoadConfig().getSectionValue('system', 'log_file')
		self.avr['maximumAllowedConnectionsPerIP'] = int(LoadConfig().getSectionValue('main','no_of_connections'))
		self.avr['maximumAllowedConnectionsPerTTL'] = int(LoadConfig().getSectionValue('ttl', 'no_ttl_connections'))
		self.avr['adminEmail'] = LoadConfig().getSectionValue('alert','admin_email')
		self.avr['whitelistIPs'] = LoadConfig().getSectionValue('main','whitelisted_ips')
		self.avr['blockTimeIP'] = LoadConfig().getSectionValue('main','block_period_ip')
		self.avr['blockTimeTTL'] = LoadConfig().getSectionValue('ttl','block_period_ttl')
		self.avr['exectime'] = int(LoadConfig().getSectionValue('main','rexec_time'))
		self.avr['montport'] = LoadConfig().getSectionValue('main','mont_port')
		self.avr['monlisten'] = LoadConfig().getSectionValue('main','mont_listen')
		self.avr['montInterface'] = LoadConfig().getSectionValue('main','mont_interface')
		self.avr['montProtocol'] = LoadConfig().getSectionValue('ttl', 'mont_protocol')
		self.avr['receiver'] = LoadConfig().getSectionValue('alert','admin_email')
		self.avr['smtpserver']= LoadConfig().getSectionValue('alert','smtp_server')
		self.avr['username'] = LoadConfig().getSectionValue('alert','smtp_user')
		self.avr['password'] = LoadConfig().getSectionValue('alert','smtp_passwd')
		self.avr['type'] = LoadConfig().getSectionValue('alert','smtp_type')

