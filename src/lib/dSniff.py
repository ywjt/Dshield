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
import subprocess, os, sys
import string
import commands, select
import datetime, time
from time import sleep
from lib.dMail import PyEmail
from lib.dLog import save_log
from lib.influxDB import DB_Conn
from lib import async
from lib import Dshield


class Sniff(Dshield):
	whileTTL = ['32','64','128','255'] #除非特定的ttl值
	keepRunning = True
	pip1 = None

	def __init__(self):
		Dshield.__init__(self)

	def __del__(self):
		self.pip1.kill()
		self.pip1 = None


	def _tcpdump(self):
		s = {}
		s['wip'] = ""
		s['port'] = ""
		for port in self.avr['montport'].split(","):
			if port:
				s['port'] = s['port'] + 'dst port {0} or '.format(port)
		for wip in self.avr['whitelistIPs'].split(","):
			if wip:
				if wip.find("~")>0:
					lstart = int(wip.split("~")[0].split(".")[-1])
					lend = int(wip.split("~")[1].split(".")[-1])+1
					ldun = ".".join(wip.split("~")[1].split(".")[0:3])
					for wli in xrange(lstart, lend):
						s['wip'] = s['wip'] + '! dst net {0} and '.format("%s.%d" % (ldun,wli))
				elif wip.find("-")>0:
					lstart = int(wip.split("-")[0].split(".")[-1])
					lend = int(wip.split("-")[1].split(".")[-1])+1
					ldun = ".".join(wip.split("-")[1].split(".")[0:3])
					for wli in xrange(lstart, lend):
						s['wip'] = s['wip'] + '! dst net {0} and '.format("%s.%d" % (ldun,wli))
				else:
					s['wip'] = s['wip'] + '! dst net {0} and '.format(wip)
		s['port'] = s['port'].strip("or ")
		s['wip']  = s['wip'].strip("and ")
		command = ['tcpdump', '-nvtqO', s['port'], 'and', s['wip']]
		if not self.avr['montInterface'] is None:
			command.insert(1, "-i%s" % self.avr['montInterface'])
		if not self.avr['montProtocol'] is None:
			command.insert(1, self.avr['montProtocol'])
		try:
			p1 = subprocess.Popen(command, bufsize=20000, stdout=subprocess.PIPE, close_fds=True)
		except Exception,e:
			save_log('ERROR',"'Sniff_tcpdump' Exception: %s" %(e))
		return p1

	def _collect(self, process, timeout):
		coll_cnt = []
		clone_coll = []
		dnct_ttls = {}
		count = None
		while process.poll() is None:
			time.sleep(0.1)
			for line in iter(process.stdout.readline,""):
				if count is None:
					timeout = int(time.time()) + timeout
				line = line.split(' ')
				strl = str(line)
				if strl.find("'ttl'") >= 0:
					if line[4].strip(',') not in self.whileTTL:
						coll_cnt.append(line[4].strip(','))
				if int(time.time()) > timeout:
					try:
						process.terminate()
						break
					except Exception,e:
						save_log('ERROR',"'Sniff_collect' Exception: %s" %(e))
				count = True
			clone_coll = set(coll_cnt)
			for item in clone_coll:
				dnct_ttls[item] = coll_cnt.count(item)
			process.communicate()
			if process.stdin:
				process.stdin.close()
			if process.stdout:
				process.stdout.close()
			if process.stderr:
				process.stderr.close()
			try:
				process.kill()
			except Exception,e:
				pass
		return dnct_ttls

	@async
	def _block(self, ttls):
		print ttls
		if self.avr['montInterface']:
			ttls.insert(2, self.avr['montInterface'])
		else:
			ttls.insert(2, "")
		json_body = [{
			"measurement": "block_ttl",
			"tags": {"ttl":ttls[0], "interface":ttls[2]},
			"fields":{"counts":float(ttls[1])}
		}]
		if str(self.avr['monlisten']) == "false":
			try:
				if not list(DB_Conn('ddos').select("select * from block_ttl where ttl = '%s'" % ttls[0])):
					DB_Conn('ddos').insert(json_body)
					self._block_act(ttls)
 					if self.avr['adminEmail']:
						self._sendmail(ttls)
			except Exception, e:
				save_log('ERROR',"'Sniff_block' Exception: %s" %(e))
		else:
			save_log('RECORD', "The TTL:%s has %s packets transmitted. Attention please!" % (ttls[0], ttls[1]))

	@async
	def _block_act(self,ttls):
		try:
			if not self.avr['montInterface']:
				os.system('/sbin/iptables -I INPUT -p tcp -m tcp --tcp-flags SYN,RST,ACK SYN -m ttl --ttl-eq %s -j DROP' % ttls[0])
			else:
				os.system('/sbin/iptables -I INPUT -i %s -p tcp -m tcp --tcp-flags SYN,RST,ACK SYN -m ttl --ttl-eq %s -j DROP' % (ttls[2],ttls[0]))
		except Exception, e:
			save_log('ERROR',"'Sniff_block_act' Exception: %s" %(e))
		save_log('LOCK',"The TTL:%s has %s packets transmitted, has been blocked." % (ttls[0], ttls[1]))

	@async
	def _unblock(self):
		for li in DB_Conn("ddos").select("select * from block_ttl where time <= now() - %s" % (self.avr['blockTimeTTL'])):
			self._unblock_act([li['ttl'],li['counts'],li['interface']])
			try:
				DB_Conn("ddos").delete("delete from block_ttl where ttl = '%s'" % li['ttl'])
			except Exception, e:
				save_log('ERROR',"'Sniff_unblock' Exception: %s" %(e))

	@async
	def _unblock_act(self, ttls):
		try:
			if not self.avr['montInterface']:
				os.system('/sbin/iptables -D INPUT -p tcp -m tcp --tcp-flags SYN,RST,ACK SYN -m ttl --ttl-eq %s -j DROP' % ttls[0])
			else:
				os.system('/sbin/iptables -D INPUT -i %s -p tcp -m tcp --tcp-flags SYN,RST,ACK SYN -m ttl --ttl-eq %s -j DROP' % (ttls[2],ttls[0]))
		except Exception, e:
			save_log('ERROR',"'Sniff_unblock_act' Exception: %s" %(e))
		save_log('UNLOCK',"TTL:%s has been unblocked." % ttls[0])

	@async
	def _sendmail(self, ttls):
		time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		send_body = "The TTL:%s record on %s,It has %s packets transmitted. Attention please!" % (ttls[0], time, ttls[1])
		return PyEmail().sendto("Dshield Alert", send_body)

	def _reblock_act(self):
		try:
			d = commands.getoutput("/sbin/iptables -nL INPUT|grep ^DROP|awk '{print $NF}'")
			for li in DB_Conn("ddos").select("select * from block_ttl"):
				if not li['ttl'] in d.split('\n'):
					if not li['interface']:
						os.system('/sbin/iptables -I INPUT -p tcp -m tcp --tcp-flags SYN,RST,ACK SYN -m ttl --ttl-eq %s -j DROP' % li['ttl'])
					else:
						os.system('/sbin/iptables -I INPUT -i %s -p tcp -m tcp --tcp-flags SYN,RST,ACK SYN -m ttl --ttl-eq %s -j DROP' % (li['interface'],li['ttl']))
					save_log('REBL','TTL:%s reload in iptables Success.' % li['ttl'])
		except Exception,e:
			save_log('ERROR',"'Sniff_reblock_act' Exception: %s" %(e))


	def run(self):
		keys = []
		while self.keepRunning:
			self._reblock_act()
			self._unblock()
			self.pip1 = self._tcpdump()
			ttls = self._collect(self.pip1, 2)
			if len(ttls) > 0:
				for key in ttls.keys():
					if ttls[key] >= self.avr['maximumAllowedConnectionsPerTTL']:
						self._block([str(key), int(ttls[key])])
						self.pip1 = None
			sleep(self.avr['exectime'])
