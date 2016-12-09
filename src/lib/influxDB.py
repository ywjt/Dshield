
from influxdb import InfluxDBClient

class DB_Conn():
	client = ''
	db = ''

	def __init__(self, db):
		try:
			self.client = InfluxDBClient('localhost', 3086, 'ddos', 'ddos', db)
		except IOError, e:
			print "InfluxDB Connected Fail ..."
			return

	def select(self, sql):
		return self.client.query(sql).get_points()

	def insert(self, json_data):
		return self.client.write_points(json_data)

	def delete(self, sql):
		return self.client.query(sql)
