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
import os
import commands
import datetime, time
from time import sleep
from lib.dMail import PyEmail
from lib.dLog import save_log
from lib.dStat import Dstat
#from lib.dSniff import Sniff
from lib.influxDB import DB_Conn
from lib import async
from lib import Dshield





class CC(Dshield):

    def __init__(self):
        Dshield.__init__(self)

    def _collect(self):
        s = {}
        ss = {}
        s['wip'] = ""
        s['port'] = ""
        ss['bin'] = "/usr/sbin/ss"
        ss['option'] = "-4tn"
        ss['state'] = "state established state fin-wait-1 state syn-recv"
        ss['column1'] = "awk -F'[ :]*' '{if (NR>1) a[$6]++}END{for(i in a){print a[i],i,$4,$5}}'"
        ss['column2'] = "awk -F'[ :]*' '{if (NR>1){a[$6\" \"$1]++}}END{for(i in a){print a[i],$4,$5,i}}'"
        for wip in self.avr['whitelistIPs'].split(","):
            if wip:
                if wip.find("~")>0:
                    lstart = int(wip.split("~")[0].split(".")[-1])
                    lend = int(wip.split("~")[1].split(".")[-1])+1
                    ldun = ".".join(wip.split("~")[1].split(".")[0:3])
                    for wli in xrange(lstart, lend):
                        s['wip'] = s['wip'] + '! dst {0} and '.format("%s.%d" % (ldun,wli))
                elif wip.find("-")>0:
                    lstart = int(wip.split("-")[0].split(".")[-1])
                    lend = int(wip.split("-")[1].split(".")[-1])+1
                    ldun = ".".join(wip.split("-")[1].split(".")[0:3])
                    for wli in xrange(lstart, lend):
                        s['wip'] = s['wip'] + '! dst {0} and '.format("%s.%d" % (ldun,wli))
                else:
                    s['wip'] = s['wip'] + '! dst {0} and '.format(wip)
        for port in self.avr['montport'].split(","):
            if port:
                s['port'] = s['port'] + 'sport = :{0} or '.format(port)
        coll_cmd  = "%s %s %s '( %s )' '( %s )'| %s" % (ss['bin'], ss['option'], ss['state'], s['wip'].strip("and "), s['port'].strip("or "), ss['column1'])
        curr_cmd = "%s %s '( %s )' '( %s )'| %s" % (ss['bin'], ss['option'], s['wip'].strip("and "), s['port'].strip("or "), ss['column2'])
        self._collect_current(commands.getoutput(curr_cmd))
        return commands.getoutput(coll_cmd)

    @async
    def _collect_current(self, data):
        if len(data)>0:
            for line in data.strip().split("\n"):
                line = line.strip().split(' ')
                if int(line[0]) < 1:
                    continue
                json_body = [{
                    "measurement":"current", 
                    "tags":{"foreaddr":line[3], "locaddr":line[1], "port":line[2], "state":line[4]},
                    "fields":{"connections":int(line[0])}
                }]
                try:
                    if not list(DB_Conn("connect").select("select * from current where foreaddr = '%s' and time >= now() - 1m" % line[3])):
                        DB_Conn("connect").insert(json_body)
                except Exception, e:
                    save_log('ERROR',"'CC_collect_current' Exception: %s" %(e))

    @async
    def _dstat(self):
            net  = Dstat().net()
            load = Dstat().loadavg()
            json_body = [{
                "measurement": "dstat",
                "tags": {"1m":load['1m'],"recv":net['recv']},
                "fields":{"1m":load['1m'], "5m":load['5m'], "15m":load['15m'], "recv":net['recv'], "send":net['send']}
            }]
            try:
                if not list(DB_Conn("system").select("select * from dstat where time >= now() - 1m")):
                    DB_Conn("system").insert(json_body)
            except Exception, e:
                save_log('ERROR',"'CC_dstat' Exception: %s" %(e))


    @async
    def _block(self, ips):
        json_body = [{
            "measurement": "block",
            "tags": {"target":ips[1], "locaddr":ips[2], "port":ips[3]},
            "fields":{"connections":float(ips[0])}
        }]
        if str(self.avr['monlisten']) == "false":
            try:
                if not list(DB_Conn('ddos').select("select * from block where target = '%s'" % ips[1])):
                    DB_Conn('ddos').insert(json_body)
                    self._block_act(ips)
                    if self.avr['adminEmail']:
                        self._sendmail(ips)
            except Exception, e:
                save_log('ERROR',"'CC_block' Exception: %s" %(e))
        else:
            save_log('RECORD', "IP addresses:%s has %s connections to server ip %s:%s." % (ips[1], ips[0], ips[2], ips[3]))

    @async
    def _block_act(self,ips):
        try:
            os.system('/sbin/iptables -I INPUT -s %s -j DROP' % ips[1])
        except Exception, e:
            save_log('ERROR',"'CC_block_act' Exception: %s" %(e))
        save_log('LOCK',"%s has been blocked, It has %s connections to server ip %s:%s." % (ips[1], ips[0], ips[2], ips[3]))
        
    @async
    def _unblock(self):
        for li in DB_Conn("ddos").select("select target,connections from block where time <= now() - %s" % (self.avr['blockTimeIP'])):
            self._unblock_act(li['target'])
            try:
                DB_Conn("ddos").delete("delete from block where target = '%s'" % li['target'])
            except Exception, e:
                save_log('ERROR',"'CC_unblock' Exception: %s" %(e))

    @async
    def _unblock_act(self, ip):
        try:
            os.system('/sbin/iptables -D INPUT -s %s -j DROP' % ip)
        except Exception, e:
            save_log('ERROR',"'CC_unblock_act' Exception: %s" %(e))
        save_log('UNLOCK',"%s has been unblocked." % ip)

    @async
    def _sendmail(self, ips):
        time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        send_body = "IP addresses:%s record on %s,It has %s connections to server ip %s:%s." % (ips[1], time, ips[0], ips[2], ips[3])
        return PyEmail().sendto("Dshield Alert",send_body)

    def _reblock_act(self):
        try:
            d = commands.getoutput("/sbin/iptables -nL INPUT|grep ^DROP|awk '{print $4}'")
            for li in DB_Conn("ddos").select("select target,connections from block"):
                if not li['target'] in d.split('\n'):
                    os.system('/sbin/iptables -I INPUT -s %s -j DROP' % li['target'])
                    save_log('REBL','%s reload in iptables Success.' % li['target'])
        except Exception,e:
            save_log('ERROR',"'CC_reblock_act' Exception: %s" %(e))


    def run(self):
        while self.keepRunning:
            self._reblock_act()
            self._unblock()
            #Sniff()._unblock()
            self._dstat()
            result = self._collect()
            if not result.strip():
                sleep(self.avr['exectime'])
                continue
            result = result.split("\n")
            for line in result:
                line = line.strip().split(' ')
                if int(line[0]) >= self.avr['maximumAllowedConnectionsPerIP']:
                    self._block(line)
            sleep(self.avr['exectime'])

