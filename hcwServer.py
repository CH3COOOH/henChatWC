# -*- coding:utf-8 -*-

# Start: 2023.03.26
# Update:

import time
import hashlib
import json
import sys

from websocket_server import WebsocketServer
from msgdb import MsgDB
import azlib.pr as apr
import errorcode

SERVER_VER = '230327'

log = apr.Log()

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

	def __reply(self, server, client, type_, payload):
		reply = {'type': type_, 'payload': payload}
		server.send_message(client, json.dumps(reply))

	def __kickoff(self, server, client):
		## Refer the source code
		client['handler'].send_close(1000, bytes('', encoding='utf-8'))
		server._terminate_client_handler(client['handler'])

	def __reply_and_kickoff(self, server, client, type_, payload):
		self.__reply(server, client, type_, payload)
		self.__kickoff(server,client)

	def when_newClient(self, client, server):
		self.online_total += 1
		client['id'] = str(time.time())
		log.print('New client comes at %s. There are %d clients online.' % (client['id'], self.online_total))

	def when_clientLeft(self, client, server):
		self.online_total -= 1
		log.print('ID: [%s] left. There are %d clients online.' % (client['id'], self.online_total))
		try:
			del(self.onlineLst[client['id']])
		except:
			log.print('ID: [%s] has already been removed.' % client['id'])

	def when_msgReceived(self, client, server, msg):

	# Coming message structure:
	# msg = {'action': 'put' or 'get',
	# 		'msg': str,
	# 		'key_hash': str,
	# 		'timeout': int,
	# 		'isOnetime': boolean
	# }
		# print(msg)
		try:
			d_msg = json.loads(msg)
		except:
			self.__reply_and_kickoff(server, client, -1, 'Unable to parse data')
			return -1

		try:
			if d_msg['action'] == 'put':
				res = self.msgdb.insert(d_msg['key_hash'], d_msg['msg'], d_msg['timeout'], d_msg['isOnetime'])
				if res == 0:
					self.__reply_and_kickoff(server, client, 0, 'OK')
				else:
					self.__reply_and_kickoff(server, client, -1, errorcode.code2msg[res])

			elif d_msg['action'] == 'get':
				msg_in_db = self.msgdb.get(d_msg['key_hash'])
				if type(msg_in_db) == str:
					self.__reply_and_kickoff(server, client, 1, msg_in_db)
				else:
					self.__reply_and_kickoff(server, client, -1, errorcode.code2msg[msg_in_db])

			else:
				self.__reply_and_kickoff(server, client, -1, 'Bad request')
		except:
			print('Error occurred.')
			self.__reply_and_kickoff(server, client, -1, 'Server error')
			return -1
		return 0

	def start(self):
		log.print('Launch a server on port %d...' % self.port)
		server = WebsocketServer(port=self.port, host=self.host)
		# server.set_fn_new_client(self.when_newClient)
		# server.set_fn_client_left(self.when_clientLeft)
		server.set_fn_message_received(self.when_msgReceived)
		server.run_forever()



def main(host, port, msgdb):
	a1 = HCWS(port, host, msgdb)
	a1.start()



if __name__ == '__main__':
	print('hcwServer <host:port> <db_fname>')
	h, p = sys.argv[1].split(':')
	mdb = MsgDB(max_n=-99, db_fname=sys.argv[2])
	main(h, int(p), msgdb=mdb)

