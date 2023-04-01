# -*- coding:utf-8 -*-

'''
+----+-------+-------+-------+
|hash|message|timeout|isOneTime|
+----+-------+-------+-------+
'''

import time
from lowestdb import LowestDB

class MsgDB:
	def __init__(self, max_n, db_fname='msgdb.db'):
		self.ldb = LowestDB([('msg', 'TEXT'), ('timeout', 'INT'), ('isOneTime', 'BOOLEAN')], table_name='HENCHATWC', max_n=max_n, db_fname=db_fname)

	def insert(self, hash_, msg, timeout, isOneTime):
		return self.ldb.insert_row(hash_, [msg, timeout, isOneTime])

	def delete(self, hash_):
		return self.ldb.delete_row_by_hash(hash_)

	def isOutdated(self, hash_):
		timeout = self.ldb.extract_value_by_hash(hash_, 'timeout')
		if (timeout != None) and (time.time() > timeout):
			return True
		else:
			return False

	def get(self, hash_):
		record = self.ldb.extract_row_by_hash(hash_)
		if record == None:
			return -0x12  ## --- Hash does not existed
		if record[2] < time.time():
			self.delete(hash_)
			return -0x11  ## --- Outdated
		msg = record[1]
		if record[3] == True:
			self.delete(hash_)
		return msg

	def get_outdated_all(self, batchSize=3):
		outdated_hash = []
		idx = 0
		while True:
			cache = self.ldb.extract_rows_by_row_num(idx, batchSize)
			if len(cache) == 0:
				break
			for r in cache:
				if r[2] < time.time():
					outdated_hash.append(r[0])
			idx += batchSize
		return outdated_hash


if __name__ == '__main__':
	mdb = MsgDB(5)
	print(mdb.insert('90da67dsfas2', 'fwqdq984dawds6ab==', time.time(), True))
	print(mdb.insert('80da6755as2s', '48aff4fdawds64fa5a==', time.time()+3600, True))
	print(mdb.insert('12da6755adsv', 'awdsf4fdawds64fa5a==', time.time()+5, False))
	time.sleep(3)
	# print(mdb.get('90da67dsfas2'))  ## -0x11
	# print(mdb.get('80da6755as2s'))
	# print(mdb.get('80da6755as2s'))  ## -0x12
	# print(mdb.get('12da6755adsv'))
	# print(mdb.get('12da6755adsv'))
	print(mdb.get_outdated_all())