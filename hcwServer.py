# -*- coding:utf-8 -*-

# Start: 2023.03.26
# Update:

import time
import hashlib
import json
import sys

from websocket_server import WebsocketServer
from msgdb import MsgDB
import azlib.ut as aut
import errorcode

SERVER_VER = '230326'
MAX_ONLINE = 15

def timeNow():
	import datetime
	now = datetime.datetime.now()
	return {'YY': now.strftime('%Y'),
			'MM': now.strftime('%m'),
			'DD': now.strftime('%d'),
			'hh': now.strftime('%H'),
			'mm': now.strftime('%M'),
			'ss': now.strftime('%S')}

def log(text):
	ct = timeNow()
	print('[%s.%s.%s-%s:%s:%s] %s' % (ct['YY'], ct['MM'], ct['DD'], ct['hh'], ct['mm'], ct['ss'], text))


def randStr(length):
	from random import choice
	randPool = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&*?@~-'
	return ''.join(choice(randPool) for _ in xrange(length))


class HCWS:

	def __init__(self, port, host, msgdb):
		self.host = host
		self.port = port
		self.onlineLst = {}
		self.msgdb = msgdb
		self.online_total = 0


	def __getClientById(self, cid):
		for i in self.onlineLst.keys():
			if cid == i:
				return self.onlineLst[i][0]
		return None


	def __reply(self, server, client, type_, payload):
		reply = {'type': type_, 'payload': payload}
		server.send_message(client, json.dumps(reply))


	def newClient(self, client, server):
		self.online_total += 1
		client['id'] = str(time.time())
		log('New client comes at %s. There are %d clients online.' % (client['id'], self.online_total))


	def clientLeft(self, client, server):
		self.online_total -= 1
		log('ID: [%s] left. There are %d clients online.' % (client['id'], self.online_total))
		try:
			del(self.onlineLst[client['id']])
		except:
			log('ID: [%s] has already been removed.' % client['id'])


	def msgReceived(self, client, server, msg):

	# Coming message structure:
	# msg = {'action': 'put' or 'get',
	# 		'msg': str,
	# 		'key_hash': str,
	# 		'timeout': int,
	# 		'isOnetime': boolean
	# }
		print(msg)
		try:
			d_msg = json.loads(msg)
			if d_msg['action'] == 'put':
				res = self.msgdb.insert(d_msg['key_hash'], d_msg['msg'], d_msg['timeout'], d_msg['isOnetime'])
				if res == 0:
					self.__reply(server, client, 0, 'OK')
				else:
					self.__reply(server, client, -1, errorcode.code2msg[res])

			elif d_msg['action'] == 'get':
				msg_in_db = self.msgdb.get(d_msg['key_hash'])
				if type(msg_in_db) == str:
					self.__reply(server, client, 1, msg_in_db)
				else:
					self.__reply(server, client, -1, errorcode.code2msg[msg_in_db])

			else:
				self.__reply(server, client, -1, 'Bad request')
		except:
			print('Error occurred.')
			self.__reply(server, client, -1, 'Server error')


	def start(self):
		log('Launch a server on port %d...' % self.port)
		server = WebsocketServer(self.port, host=self.host)
		server.set_fn_new_client(self.newClient)
		server.set_fn_client_left(self.clientLeft)
		server.set_fn_message_received(self.msgReceived)
		server.run_forever()



def main(host, port, msgdb):
	a1 = HCWS(port, host, msgdb)
	a1.start()



if __name__ == '__main__':
	mdb = MsgDB(9999)
	if len(sys.argv) < 2:
		main(host='127.0.0.1', port=9002, msgdb=mdb)
	else:
		h, p = sys.argv[1].split(':')
		main(h, int(p), msgdb=mdb)

