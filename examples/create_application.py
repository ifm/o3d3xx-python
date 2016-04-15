import o3d3xx
import sys
import time

if len(sys.argv) > 1:
	address=sys.argv[1]
else:
	address='192.168.0.69'

# create device
device = o3d3xx.Device(address)

# open a session and create an application for editing
session = device.requestSession()
session.startEdit()
print(session)
applicationIndex = session.edit.createApplication()
print(applicationIndex)
print(session)
print(session.edit)
session.edit.editApplication(applicationIndex)

# configure the application to
# - double exposure
session.edit.imagerConfig.changeType("under5m_moderate")
# - free-run at 10 Hz
session.edit.application.setParameter("TriggerMode", "1")
session.edit.imagerConfig.setParameter("FrameRate", "10")
# and perform an auto-exposure run to determine
# exposure times
session.edit.imagerConfig.startCalculateExposureTime()
# wait until the auto-exposure process has finished
while session.edit.imagerConfig.getProgressCalculateExposureTime() < 1.0:
	time.sleep(1)
# name and save the application and stop editing
session.edit.application.setParameter("Name", "o3d3xx-python example application")
session.edit.application.save()
session.edit.stopEditingApplication()

# set the new application as active and save the change
session.edit.device.setParameter("ActiveApplication", str(applicationIndex))
session.edit.device.save()

# finish the session
session.cancelSession()
