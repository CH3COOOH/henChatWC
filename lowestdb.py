# -*- coding:utf-8 -*-

import os
import sqlite3

from azlib.pr import Log

class LowestDB:
	def __init__(self, columns, db_fname='lowtable.db', table_name='LOWTABLE', max_n=-99):
		self.log = Log()
		self.max_n = max_n
		self.db_fname = db_fname
		self.table_name = table_name
		self.hash_map = {}
		self.columns = columns  ## [(label1, dtype1), (label2, dtype2), ...]
		if os.path.exists(db_fname) == False:
			self.__initDB()
	
	def __initDB(self):
		sql_cmd = f'CREATE TABLE {self.table_name}('
		sql_cmd += f'\nHASH TEXT PRIMARY KEY NOT NULL,'
		for label, dtype in self.columns:
			sql_cmd += f'\n{label} {dtype} NOT NULL,'
		sql_cmd = sql_cmd[:-1] + ');'
		print(sql_cmd)

		conn = sqlite3.connect(self.db_fname)
		c = conn.cursor()
		c.execute(sql_cmd)
		conn.commit()
		conn.close()
		self.log.print('New database created.')
		return 0

	def __cmd_selectXFromWhereYeq_(self, X, Y):
		return f"SELECT {X} FROM {self.table_name} WHERE {Y}=?"

	def __cmd_insertIntoValues_(self):
		cmd_values = ''
		for i in range(len(self.columns)+1):
			cmd_values += '?,'
		return f"INSERT INTO {self.table_name} VALUES ({cmd_values[:-1]})"
	
	def __cmd_deleteFromWhereXeq_(self, X):
		return f"DELETE FROM {self.table_name} WHERE {X}=?"

	def __isReachLimitation(self, c):
		dbsize = list(c.execute(f"SELECT COUNT(*) FROM {self.table_name}"))[0][0]
		if dbsize == self.max_n:
			return True
		else:
			return False

	def insert_row(self, hash_, values):
		if len(values) != len(self.columns):
			return -0x02  ## --- Different column amount

		conn = sqlite3.connect(self.db_fname)
		c = conn.cursor()
		if self.__isReachLimitation(c):
			conn.close()
			return -0x01  ## --- Over max size
		try:
			hash_values = [hash_]
			hash_values.extend(values)
			c.execute(self.__cmd_insertIntoValues_(), hash_values)
			conn.commit()
		except sqlite3.IntegrityError:
			conn.close()
			return -0x03  ## --- Hash existed or something else

		conn.close()
		return 0

	def delete_row_by_hash(self, hash_):
		conn = sqlite3.connect(self.db_fname)
		c = conn.cursor()
		if len(list(c.execute(self.__cmd_selectXFromWhereYeq_('HASH', 'HASH'), (hash_, )))) == 0:
			conn.close()
			return -0x04
		c.execute(self.__cmd_deleteFromWhereXeq_('HASH'), (hash_, ))
		conn.commit()
		conn.close()
		return 0

	def extract_value_by_hash(self, hash_, col_name):
		conn = sqlite3.connect(self.db_fname)
		c = conn.cursor()
		res = list(c.execute(self.__cmd_selectXFromWhereYeq_(col_name, 'HASH'), (hash_, )))
		conn.close()
		if len(res) == 0:
			return None
		else:
			return res[0][0]
	
	def extract_row_by_hash(self, hash_):
		conn = sqlite3.connect(self.db_fname)
		c = conn.cursor()
		res = list(c.execute(self.__cmd_selectXFromWhereYeq_('*', 'HASH'), (hash_, )))
		conn.close()
		if len(res) == 0:
			return None
		else:
			return res[0]	
	
	def _inner_fun_test(self):
		print(self.__cmd_select_FromWhere_eq_())
		print(self.__cmd_insertIntoValues_())
		print(self.__cmd_deleteFromWhere_eq_())



if __name__ == '__main__':
	print('[Initiate DB]')
	ldb = LowestDB(columns=[('MSG', 'TEXT'), ('TIMEOUT', 'INT')], max_n=-99)
	print('[Insert]')
	print(ldb.insert_row('90da67dsfas2', ['😀🥵', '114514']))
	print(ldb.insert_row('80da6755as2s', ['🥰🤤', '114515']))
	print(ldb.insert_row('8v9wedsjdfdge', ['🥰🤤', '114515']))
	print(ldb.insert_row('90da67dsfas2', ['fwqdq984dawds6ab==', '114516']))
	print('[Extract]')
	print(ldb.extract_value_by_hash('90da67dsfas2', 'MSG'))
	print('[Inject]')
	print(ldb.extract_value_by_hash("*'", 'MSG'))
	print('[Delete]')
	print(ldb.delete_row_by_hash('90da67dsfas2'))
	print(ldb.delete_row_by_hash('80da6755as2s'))
	print(ldb.delete_row_by_hash('Unexist'))
	print(ldb.extract_value_by_hash('90da67dsfas2', 'MSG'))
#	print(ldb.insert_row('90da67dsfas2', ['😀🥵', '114514']))
#	print(ldb.insert_row('80da6755as2s', ['🥰🤤', '114515']))
#	print(ldb.insert_row('8v9wedsjdfdge', ['🥰🤤', '114515']))

#	ldb._inner_fun_test()