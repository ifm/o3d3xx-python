import o3d3xx
import sys

if len(sys.argv) > 1:
	address=sys.argv[1]
else:
	address='192.168.0.69'

device = o3d3xx.Device(address)
session = device.requestSession()
session.startEdit()
session.edit.createApplication()
session.cancelSession()
