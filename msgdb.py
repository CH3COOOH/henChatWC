# -*- coding:utf-8 -*-

'''
+----+-------+-------+
|hash|message|timeout|
+----+-------+-------+
'''

import time
from lowestdb import LowestDB

class MsgDB:
	def __init__(self, max_n):
		self.ldb = LowestDB(['msg', 'timeout'], max_n=max_n)

	def insert(self, hash_, msg, timeout):
		return self.ldb.insert_row(hash_, [msg, timeout])

	def delete(self, hash_):
		return self.ldb.delete_row(hash_)

	def isOutdated(self, hash_):
		timeout = self.ldb.extract_value(hash_, 'timeout')
		if (timeout != None) and (time.time() > timeout):
			return True
		else:
			return False

	def get(self, hash_):
		if self.isOutdated(hash_):
			self.delete(hash_)
			return -0x01
		msg = self.ldb.extract_value(hash_, 'msg')
		self.delete(hash_)
		if msg == None:
			return -0x02  ## --- Hash not existed
		return msg

if __name__ == '__main__':
	mdb = MsgDB(2)
	print(mdb.insert('90da67dsfas2', 'fwqdq984dawds6ab==', time.time()))
	print(mdb.insert('80da6755as2s', '48aff4fdawds64fa5a==', time.time()+3600))
	print(mdb.insert('12da6755adsv', 'awdsf4fdawds64fa5a==', time.time()+3600))
	time.sleep(3)
	print(mdb.get('90da67dsfas2'))
	print(mdb.get('80da6755as2s'))
	print(mdb.get('80da6755as2s'))
	print(mdb.get('12da6755adsv'))