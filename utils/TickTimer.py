import time


class TickTimer:
	# Interval in milliseconds
	"""
	TickTimer gives a tick interval timer for periodic actions on a fixed interval in ms

	@param interval in ms
	"""
	def __init__(self, interval: int):
		self.interval: int = interval * 1000000
		self.tick: int = time.perf_counter_ns()
		self.tock: int = 0
		self.delta: float = 0.0

	def check(self) -> bool:
		self.tock = time.perf_counter_ns()
		if self.tock - self.tick >= self.interval:
			self.delta = (self.tock - self.tick) / 1000000000
			self.tick = self.tock
			return True
		else:
			return False

	# Returns frame delta as a float in fractional seconds since last frame
	def getDelta(self) -> float:
		return self.delta


class DeltaTimer:
	"""
	DeltaTimer is used to keep track of a frame delta time
	"""
	def __init__(self):
		self.tick: int = time.perf_counter_ns()
		self.tock: int = 0
		self.delta: float = 0.0

	"""
	getDelta returns a float of seconds since the last getDelta call
	Use once per loop per instance to get a frame delta time for impulse calculations
	"""
	def getDelta(self) -> float:
		self.tock = time.perf_counter_ns()
		self.delta = (self.tock - self.tick) / 1000000000
		self.tick = time.perf_counter_ns()
		return self.delta
