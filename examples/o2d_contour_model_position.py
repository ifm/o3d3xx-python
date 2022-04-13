from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import o3d3xx
import sys
import json

# First parameter is the IP address of the camera

if len(sys.argv) > 1:
	address=sys.argv[1]
else:
	address='192.168.0.69'

pcic = o3d3xx.ImageClient(address, 50010)

# This example works for applications where the first model is a
# "contour detection" model that contains only a single ROI.
# If the contour is found, its position, rotation and score are
# extracted from the overall application result.

# repeatedly read frames from the process interface
while True:
	result = pcic.readNextFrame()
	if 'jsonResult' in result:
		jsonResult = json.loads(result['jsonResult'].tobytes().decode("utf-8"))
		contourResult = jsonResult["Models"][0]["Result"]
		if contourResult["all_groups_passed"]:
			firstRoiResult = contourResult["groups"][0]["matches_list_pass"][0]
			x = firstRoiResult["column"]
			y = firstRoiResult["row"]
			angle = firstRoiResult["angle"]
			score = firstRoiResult["score"]
			print("Found contour at (%.01f, %.01f), angle %.01f with score %.03f" % (x, y, angle, score))
		else:
			print("Contour not found")
	else:
		print("No application result found")
