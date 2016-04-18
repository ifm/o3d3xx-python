from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import o3d3xx
import sys
import time

if len(sys.argv) > 1:
	address=sys.argv[1]
else:
	address='192.168.0.69'

pcic = o3d3xx.ImageClient(address, 50010)
pcic.debug = True

# repeatedly read frames from the process interface
lasttimestamp = time.time()
startTimestamp = lasttimestamp
frameCounter = 0

while True:
	result = pcic.readNextFrame()
	if 'diagnostic' in result:
		print(result['diagnostic'])
	frameCounter = frameCounter + 1

	# timing
	timestamp = time.time()
	timediff = timestamp - lasttimestamp
	print('Current frame time: %f (%f fps), bandwidth %f MBit/s' % (timediff, 1.0/timediff, 8 * pcic.recvCounter / (1e6 * timediff)))
	print('Overall run time: %f for %d frames (%f fps)' % (timestamp - startTimestamp, frameCounter, (frameCounter * 1.0)/(timestamp - startTimestamp)))

	lasttimestamp = timestamp
	pcic.recvCounter = 0


