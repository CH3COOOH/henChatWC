import time

class Timer:
	def __init__(self, period):
		self.period = period
		self.st = -1

	def startpoint(self):
		self.st = time.time()

	def endpoint(self):
		dt = time.time() - self.st
		wt = self.period - dt
		if wt < 0:
			wt = 0
		time.sleep(wt)
