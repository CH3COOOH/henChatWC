# -*- coding:utf-8 -*-

import os
import sqlite3

from azlib.pr import Log

class LowestDB:
	def __init__(self, columns, db_fname='lowtable.db', table_name='LOWTABLE', max_n=-99):
		self.log = Log()
		self.row_ctr = max_n
		self.db_fname = db_fname
		self.table_name = table_name
		self.hash_map = {}
		self.columns = columns  ## [(label1, dtype1), (label2, dtype2), ...]
		# self.columns = self.__index_columns(columns)
		if os.path.exists == False:
			return self.__initDB()
	
	def _initDB(self):
		sql_cmd = f'CREATE TABLE {self.table_name}('
		isHead = True
		for label, dtype in self.columns:
			if isHead:
				sql_cmd += f'\n{label} {dtype} PRIMARY KEY NOT NULL,'
				isHead = False
			else:
				sql_cmd += f'\n{label} {dtype} NOT NULL,'
		sql_cmd = sql_cmd[:-1] + ');'
		print(sql_cmd)

		# conn = sqlite3.connect(self.db_fname)
		# c = conn.cursor()
		# c.execute(sql_cmd)
		# conn.commit()
		# conn.close()
		# self.log.print('New database created.')
		# return 0

	def _cmd_selectFromWhere(self, column_1, table, column_2, value):
		if type(value) == str:
			return f"SELECT {column_1} FROM {table} WHERE {column_2}='{value}'"
		else:
			return f"SELECT {column_1} FROM {table} WHERE {column_2}={value}"

	def _cmd_insertIntoValues(self, table, values):
		cmd_values = ''
		for i in range(len(values)):
			if self.columns[i][1] == 'TEXT':
				cmd_values += f"'{values[i]}',"
			else:
				cmd_values += f"{values[i]},"
		return f"INSERT INTO {table} VALUES ({cmd_values[:-1]})"

	def __isReachLimitation(self):
		if self.row_ctr == 0:
			return True
		else:
			return False

	def __isIDExisted(self, target_id, c):
		if len(list(c.execute(__cmd_selectFromWhere('*', self.table_name, self.columns[0][0], target_id)))) != 0:
			return True
		else:
			return False



	def insert_row(self, hash_, values):
		if self.__isReachLimitation():
			return -0x01  ## --- Over max size
		if len(values) != len(self.columns.keys()):
			return -0x02  ## --- Different column amount

		conn = sqlite3.connect(self.db_fname)
		c = conn.cursor()
		if self.__isIDExisted(hash_, c):
			conn.close()
			return -0x03  ## --- Hash existed


		# if (hash_ in self.hash_map.keys()) == False:
		# 	self.hash_map[hash_] = values

		return 0

			

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
	ldb = LowestDB([('msg', 'TEXT'), ('timeout', 'INT')])
	# print(ldb.insert_row('90da67dsfas2', ['fwqdq984dawds6ab==', '114514']))
	# print(ldb.insert_row('80da6755as2s', ['48aff4fdawds64fa5a==', '114515']))
	# print(ldb.extract_value('90da67dsfas2', 'msg'))
	# ldb.delete_row('90da67dsfas2')
	# print(ldb.extract_value('90da67dsfas2', 'msg'))
	ldb._initDB()
	print(ldb._cmd_selectFromWhere('*', ldb.table_name, ldb.columns[0][0], 'ac024f29'))
	print(ldb._cmd_insertIntoValues(ldb.table_name, ['helllo world', 100]))