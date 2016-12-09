#!/usr/bin/env python
# encoding=utf-8

import sys
sys.path.append("..")
from lib.influxUnit import DB_Conn


if __name__ == '__main__':

	json_body = [{
		"measurement": "current",
		"tags": {"foreaddr": "6.6.6.6","locaddr":"42.62.106.245","port":"80","state":"ESTABLISHED"},
		"fields":{"connections":800, "value":300}
	}]

	print "-------------- test insert -----------------"
	if DB_Conn('connect').insert(json_body):
		print "Insert True."
	else:
		print "Insert False."

	print "-------------- test select -----------------"
	for items in DB_Conn('connect').select("select * from current"):
		print items

	print "-------------- test delete -----------------"
	try:
		DB_Conn('connect').delete("delete from current where foreaddr = '6.6.6.6'")
	except IOError, e:
		print "Delete Fail."
		pass
	else:
		for items in DB_Conn('connect').select("select * from current"):
			print items