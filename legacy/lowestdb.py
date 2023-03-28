# -*- coding:utf-8 -*-

class LowestDB:
	def __init__(self, columns, max_n=0):
		self.max_n = max_n
		self.hash_map = {}
		self.columns = self.__index_columns(columns)
		
	def __index_columns(self, column_names):
		columns_index = {}
		i = 0
		for c in column_names:
			columns_index[c] = i
			i += 1
		return columns_index

	def insert_row(self, hash_, values):
		if (self.max_n > 0) and (len(self.hash_map.keys()) == self.max_n):
			return -0x01  ## --- Over max size
		if len(values) != len(self.columns.keys()):
			return -0x02  ## --- Different column amount
		if (hash_ in self.hash_map.keys()) == False:
			self.hash_map[hash_] = values
			return 0
		else:
			return -0x03  ## --- Hash existed

	def delete_row(self, hash_):
		if hash_ in self.hash_map.keys():
			del self.hash_map[hash_]
			return 0
		else:
			return -0x04

	def extract_value(self, hash_, col):
		if hash_ in self.hash_map.keys():
			return self.hash_map[hash_][self.columns[col]]
		else:
			return None



if __name__ == '__main__':
	ldb = lowDB(['msg', 'timeout'])
	print(ldb.insert_row('90da67dsfas2', ['fwqdq984dawds6ab==', '114514']))
	print(ldb.insert_row('80da6755as2s', ['48aff4fdawds64fa5a==', '114515']))
	print(ldb.extract_value('90da67dsfas2', 'msg'))
	ldb.delete_row('90da67dsfas2')
	print(ldb.extract_value('90da67dsfas2', 'msg'))
