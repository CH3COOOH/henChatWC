## Last update: 2023.02.04
import hashlib
import base64

def sif(condition, value_true, value_false):
	if condition:
		return value_true
	else:
		return value_false

def gracefulRead(fname, method='r'):
	with open(fname, method) as o:
		buf = o.read()
	return buf

def gracefulWrite(fname, buff, method='w'):
	try:
		with open(fname, method) as o:
			o.write(buff)
		return 0
	except:
		return -1

def str2md5(plainText):
	hl = hashlib.md5()
	hl.update(base64.b64encode(plainText.encode('utf-8')))
	return hl.hexdigest()

def str2sha1(plainText):
	hl = hashlib.sha1()
	hl.update(base64.b64encode(plainText.encode('utf-8')))
	return hl.hexdigest()