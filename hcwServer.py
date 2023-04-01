# -*- coding:utf-8 -*-

'''
Start: 2023.03.26
Update:
2023.03.31: Add policy for message length and timeout
2023.04.01: Add outdated message cleaner thread
'''

import time
import json
import sys
import threading

from websocket_server import WebsocketServer
from msgdb import MsgDB
import azlib.pr as apr
import errorcode

SERVER_VER = '230401'

log = apr.Log()

class HCWS:

	def __init__(self, port, host, msgdb):
		self.host = host
		self.port = port
		self.msgdb = msgdb

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
	
	def __policy_outdate(self, outdate):
		if outdate - time.time() > 172800.:
			return False
		return True

	# def __clean_timeout(self):
		

	def __when_msgReceived(self, client, server, msg):
	# Coming message structure:
	# msg = {'action': 'put' or 'get',
	# 		'msg': str,
	# 		'key_hash': str,
	# 		'timeout': int,
	# 		'isOnetime': boolean
	# }

		## -- Forbid big data
		if len(msg) > 4096:
			self.__reply_and_kickoff(server, client, -1, '<Data is too big>')
			return -1

		try:
			d_msg = json.loads(msg)
		except:
			## -- Bad format
			self.__reply_and_kickoff(server, client, -1, '<Unable to parse data>')
			return -1

		try:
			if d_msg['action'] == 'put':
				if self.__policy_outdate(d_msg['timeout']) == False:
					## -- Timeout set too long
					self.__reply_and_kickoff(server, client, -1, '<Invalid timeout>')
					return -1
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
				self.__reply_and_kickoff(server, client, -1, '<Bad request>')
		except:
			print('Error occurred.')
			self.__reply_and_kickoff(server, client, -1, '<Server error>')
			return -1
		return 0

	def __auto_clean_daemon(self, period, batchSize):
		## Clean outdated messages
		log.print('Outdated cleaner launched...')
		while True:
			target_hash = self.msgdb.get_outdated_all(batchSize=batchSize)
			for h in target_hash:
				log.print(f"Cleanning outdated hash: {h}")
				self.msgdb.delete(h)
			time.sleep(period)


	def start(self):
		print('henChatWC_%s' % SERVER_VER)
		log.print('Launch a server on port %d...' % self.port)
		## Server config
		server = WebsocketServer(port=self.port, host=self.host)
		server.set_fn_message_received(self.__when_msgReceived)
		## Daemon config
		t_daemon = threading.Thread(target=self.__auto_clean_daemon, args=(30, 10,))
		## Start all
		t_daemon.start()
		server.run_forever()

def main(host, port, msgdb):
	a1 = HCWS(port, host, msgdb)
	a1.start()



if __name__ == '__main__':
	print('hcwServer <host:port> <db_fname>')
	h, p = sys.argv[1].split(':')
	mdb = MsgDB(max_n=-99, db_fname=sys.argv[2])
	main(h, int(p), msgdb=mdb)

