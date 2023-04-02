# -*- coding:utf-8 -*-

'''
Start: 2023.03.26
Update:
2023.03.31: Add policy for message length and timeout
2023.04.01: Add outdated message cleaner thread
2023.04.02: Add client controller (control the message frequency)
'''

import time
import json
import sys
import threading

from websocket_server import WebsocketServer
from msgdb import MsgDB
import azlib.pr as apr
import azlib.tidyTimer as ttm
import errorcode

SERVER_VER = '230401'
CLIENT_FREQ_INTERVAL = 3. ## Allow N requests in 5s
MIN_BLOCKTIME = 60.  ## Block bad guys for N seconds
MAX_CLIENT = 1024
MAX_MSG_OUTDATE = 172800.  ## 48h

log = apr.Log()

class HCWS:

	def __init__(self, port, host, msgdb, maxPerConn):
		self.host = host
		self.port = port
		self.msgdb = msgdb
		self.maxClient = MAX_CLIENT
		self.maxPerConn = maxPerConn
		self.ip_map = {}  ## {addr: [start_time, ctr]}
		self.block_map = {}  ## {addr: timeout}

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
		if outdate - time.time() > MAX_MSG_OUTDATE:
			return False
		return True

	def __getAddrFromClient(self, client):
		return client['address'][0]

	def __isAddrBlocked(self, addr):
		if addr in self.block_map.keys():
			return True
		return False

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

	def __when_newClient(self, client, server):		
		nClient = len(server.clients)
		if nClient == self.maxClient:
			log.print('Number of clients reaches limitation!')
			self.__reply_and_kickoff(server, client, -1, '<Too many connections now. Wait for a moment...>')
			server.deny_new_connections()
			time.sleep(10.)
			server.allow_new_connections()
			log.print('Restriction stopped.')
		else:
			log.print(f"New client connected. {nClient} clients now.")

		addr = self.__getAddrFromClient(client)
		log.print(f"Client IP: {addr}")
		if self.__isAddrBlocked(addr) == True:
			log.print(f"** {addr} is a blocked address.")
			self.__reply_and_kickoff(server, client, -1, f"<You have been blocked for {MIN_BLOCKTIME} (at least) seconds!>")
			self.block_map[addr] = time.time() + MIN_BLOCKTIME
			return -1
		if addr in self.ip_map.keys():
			self.ip_map[addr][1] += 1
			if self.ip_map[addr][1] > self.maxPerConn:
				self.__reply_and_kickoff(server, client, -1, '**\nWhat are you doing? Intentional or accidental?\n**')
				self.block_map[addr] = time.time() + MIN_BLOCKTIME
				log.print(f"{addr} is blocked.")
				return -1
		else:
			self.ip_map[addr] = [time.time(), 1]
		return 0
	
	def __when_quitClient(self, client, server):
		# print(self.ip_map)
		# print(self.block_map)
		pass

	def __daemon_cleanOutdayedMsg(self, period, batchSize):
		## Clean outdated messages
		log.print('Daemon: outdated cleaner launched...')
		timer = ttm.Timer(period)
		while True:
			timer.startpoint()
			## Clean outdated messages
			target_hash = self.msgdb.get_outdated_all(batchSize=batchSize)
			for h in target_hash:
				log.print(f"Cleanning outdated hash: {h}")
				self.msgdb.delete(h)
			timer.endpoint()
	
	def __daemon_clientFreqCtrl(self, period):
		log.print('Daemon: client controller launched...')
		time.sleep(period)
		timer = ttm.Timer(period)
		while True:
			timer.startpoint()
			outdated = []
			for ip in self.ip_map.keys():
				if time.time() - self.ip_map[ip][0] > CLIENT_FREQ_INTERVAL:
					outdated.append(ip)
			for ip in outdated:
				del self.ip_map[ip]
			## Clean blacklist
			outdated = []
			for ip in self.block_map.keys():
				if time.time() > self.block_map[ip]:
					log.print(f"Will remove {ip} from blocklist.")
					outdated.append(ip)
			for ip in outdated:
				del self.block_map[ip]
			timer.endpoint()

	def start(self):
		print('henChatWC_%s' % SERVER_VER)
		log.print('Launch a server on port %d...' % self.port)

		## Server config
		server = WebsocketServer(port=self.port, host=self.host)
		server.set_fn_message_received(self.__when_msgReceived)
		server.set_fn_new_client(self.__when_newClient)
		server.set_fn_client_left(self.__when_quitClient)

		## Daemon config
		t_daemon = threading.Thread(target=self.__daemon_cleanOutdayedMsg, args=(30, 10,))
		c_daemon = threading.Thread(target=self.__daemon_clientFreqCtrl, args=(5,))

		## Start all
		t_daemon.start()
		c_daemon.start()
		server.run_forever()

def main(host, port, msgdb, maxPerConn):
	a1 = HCWS(port, host, msgdb, maxPerConn)
	a1.start()



if __name__ == '__main__':
	print('hcwServer <host:port> <db_fname>')
	h, p = sys.argv[1].split(':')
	mdb = MsgDB(max_n=-99, db_fname=sys.argv[2])
	main(h, int(p), msgdb=mdb, maxPerConn=3)

