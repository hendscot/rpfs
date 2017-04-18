import time, pigpio

fo = open("randtimegeiger.txt", "a")

def mycb(x,y,z):
	t = time.time()
	print t
	fo.write(str(t) + '\n')
	fo.flush()

pin = pigpio.pi()
cb = pin.callback(23, pigpio.FALLING_EDGE, mycb)

while 1:
	time.sleep(15)
