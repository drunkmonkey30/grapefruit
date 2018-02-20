

# storage area and manager for LEDs 
# functionality for adding leds, changing their color
# also provides the bytearray used to send it across the i2c bus
class LedManager:
	numLeds 	= 0
	ledValues	= bytearray()

	# initialize led manager with specified number of leds
	# initial color of leds is 0,0,0 (off)
	def __init__(self, n = 0):
		for i in range(n):
			self.addLed()


	# add an led with specified color
	def addLed(self, r = 0, g = 0, b = 0):
		self.ledValues.append(0); self.ledValues.append(0); self.ledValues.append(0)
		self.set_color(self.numLeds, r, g, b)
		self.numLeds += 1


	# set the color of an led
	# clamps values between 0 and 255 because the bytearray will 
	# throw an error (crash the script) if outside this range
	def set_color(self, led, r, g, b):
		if r < 0: r = 0
		if r > 255: r = 255

		if g < 0: g = 0
		if g > 255: g = 255

		if b < 0: b = 0
		if b > 255: b = 255

		#print(led, r, g, b)

		self.ledValues[3*led] 	= r
		self.ledValues[3*led+1] = g
		self.ledValues[3*led+2] = b

	# get rgb values of specified led
	# DOES NOT DO BOUNDS CHECKING
	def getColor(self, led):
		return self.ledValues[3*led], self.ledValues[3*led+1], self.ledValues[3*led+2]


	# change a color by a positive or negative value
	# NO BOUNDS CHECKING
	def modifyColor(self, led, mod_r, mod_g, mod_b):
		r, g, b = self.getColor(led)
		self.set_color(led, r+mod_r, g+mod_g, b+mod_b)

	# set color of led to all zeros (turns led off)
	# DOES NOT DO BOUNDS CHECKING
	def turnOff(self, led):
		self.set_color(led, 0, 0, 0)

	# get the RGB value of a certain led
	def printLedValue(self, led):
		if not self.ledExists(led):
			return

		r, g, b = self.getColor(led)
		print("led#" + str(led) + " R:" + str(r) +
								  " G:" + str(g) +
								  " B:" + str(b))

	def ledExists(self, led):
		if (led >= self.numLeds):
			print("*** ERROR: led #" + str(led) + " is larger than numLeds: " + str(self.numLeds))
			return False

		return True

	def speedTest(self):
		for i in range(self.numLeds):
			self.modifyColor(i, i, -i, 1)



# module tests
if __name__ == "__main__":
	lm = LedManager()
	print("default constructor:")
	print("number of leds: " + str(lm.numLeds))

	print("\nLedManager(5)")
	lm = LedManager(5)
	print("number of leds: " + str(lm.numLeds))

	print("\nadd 255 128 50")
	lm.addLed(255, 128, 50)
	print("number of leds: " + str(lm.numLeds))

	print("\nled values [0 .. 10]")
	for i in range(10):
		lm.printLedValue(i)

	print("\nset color #1")
	lm.set_color(1, 100, 100, 100)
	print("led values")
	for i in range(lm.numLeds):
		lm.printLedValue(i)

	print("\nturn off #1")
	lm.turnOff(1)
	for i in range(lm.numLeds):
		lm.printLedValue(i)

	print("\nspeed test without timeit, updating 64 leds, 100 iterations")
	import time
	lm = LedManager(64)
	total_time = 0
	for i in range(100):
		start = time.clock()
		for led in range(lm.numLeds):
			lm.set_color(led, led, led, led)
		end = time.clock()
		total_time += end - start
	print("average time: " + str(total_time/100))

	print("\nspeed test without timeit, modifying 64 leds, 100 iterations")
	lm = LedManager(64)
	total_time = 0
	for i in range(100):
		start = time.clock()
		for led in range(lm.numLeds):
			lm.modifyColor(led, 20, -20, 5)
		end = time.clock()
		total_time += end - start
	print("average time: " + str(total_time/100))


	import timeit
	print("\nspeed test with timeit, updating 64 leds")
	print("1 iteration")
	print(timeit.timeit(stmt='lm.speedTest()', setup='from __main__ import LedManager; lm = LedManager(64)', number=1))
	print("10 iteration")
	print(timeit.timeit(stmt='lm.speedTest()', setup='from __main__ import LedManager; lm = LedManager(64)', number=10))
	print("100 iteration")
	print(timeit.timeit(stmt='lm.speedTest()', setup='from __main__ import LedManager; lm = LedManager(64)', number=100))

	print("\nspeed test with timeit, updating 256 leds")
	print("1 iteration")
	print(timeit.timeit(stmt='lm.speedTest()', setup='from __main__ import LedManager; lm = LedManager(256)', number=1))
	print("10 iteration")
	print(timeit.timeit(stmt='lm.speedTest()', setup='from __main__ import LedManager; lm = LedManager(256)', number=10))
	print("100 iteration")
	print(timeit.timeit(stmt='lm.speedTest()', setup='from __main__ import LedManager; lm = LedManager(256)', number=100))

	