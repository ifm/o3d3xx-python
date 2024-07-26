import o3d3xx
import sys
import time

if len(sys.argv) > 1:
    address = sys.argv[1]
else:
    address = '192.168.0.99'

ifm_app_name = "o3d3xx-python example extrinsic calibration"
# create device
ifm_device = o3d3xx.Device(address)

# Try to find our ifm application on device; if it's not there, we're going to install it.
ifm_app_index = None
ifm_apps = ifm_device.rpc.getApplicationList()
for i, ifm_app in enumerate(ifm_apps, start=1):
    if ifm_app['Name'] == ifm_app_name:
        print(f'ifm application found on camera: {ifm_app_name}')
        ifm_app_index = i
        break

# open a session and create an application for editing
session = ifm_device.requestSession()
session.startEdit()

if not ifm_app_index:
    ifm_app_index = session.edit.createApplication()

application = session.edit.editApplication(ifm_app_index)

# configure the application to
# - double exposure
application.imagerConfig.changeType("under5m_moderate")
# - process interface trigger
application.setParameter("TriggerMode", "2")
# and perform an auto-exposure run to determine
# exposure times
application.imagerConfig.startCalculateExposureTime()
# wait until the auto-exposure process has finished
while application.imagerConfig.getProgressCalculateExposureTime() < 1.0:
    time.sleep(1)
# name and save the application and stop editing
application.setParameter("Name", "o3d3xx-python example extrinsic calibration")

application.save()
session.edit.stopEditingApplication()

# translation in [mm]
session.edit.device.setParameter('ExtrinsicCalibTransX', '42.1')
session.edit.device.setParameter('ExtrinsicCalibTransY', '44.2')
session.edit.device.setParameter('ExtrinsicCalibTransZ', '46.3')
# rotation in [degree]
session.edit.device.setParameter('ExtrinsicCalibRotX', '5.6')
session.edit.device.setParameter('ExtrinsicCalibRotY', '7.8')
session.edit.device.setParameter('ExtrinsicCalibRotZ', '9.1')

# set the new application as active and save the change
session.edit.device.setParameter("ActiveApplication", str(ifm_app_index))
session.edit.device.save()

# finish the session
session.cancelSession()

# create image client for retrieving the unit vector matrix
device = o3d3xx.ImageClient(address=address, port=50010)

# trigger device
device.sendCommand(cmd="t")
# read frames
frames = device.readNextFrame()

test = frames['extrinsicCalibration']
tX = frames['extrinsicCalibration'].transX
tY = frames['extrinsicCalibration'].transY
tZ = frames['extrinsicCalibration'].transZ

# calculate the X,Y,Z coordinates and compare them to the sensor X,Y,Z
dist = frames['distance']
unitVec = frames['unitVectors']
sensorX = frames['x']
sensorY = frames['y']
sensorZ = frames['z']

for pixIdx in range(len(dist)):
    x = 0
    y = 0
    z = 0
    if dist[pixIdx] != 0:  # only for valid values
        x = round(unitVec[pixIdx*3+0] * dist[pixIdx] + tX)
        y = round(unitVec[pixIdx*3+1] * dist[pixIdx] + tY)
        z = round(unitVec[pixIdx*3+2] * dist[pixIdx] + tZ)

    # Test the cartesian values for similarity.
    # We do not expect exact equality due to round off
    # errors.
    assert(abs(sensorX[pixIdx]-x) <= 1 and
           abs(sensorY[pixIdx]-y) <= 1 and
           abs(sensorZ[pixIdx]-z) <= 1)

print("Test passed")
