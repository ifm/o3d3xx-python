from __future__ import (absolute_import, division, print_function)
from builtins import *
import struct
import array

from .client import PCICV3Client

class ImageClient(PCICV3Client):
	def __init__(self, address, port):
		super(ImageClient, self).__init__(address, port)
		# disable all result output
		self.sendCommand("p0")
		# format string for all images
		pcicConfig = "{ \"layouter\": \"flexible\", \"format\": { \"dataencoding\": \"ascii\" }, \"elements\": [ { \"type\": \"string\", \"value\": \"star\", \"id\": \"start_string\" }, { \"type\": \"blob\", \"id\": \"normalized_amplitude_image\" }, { \"type\": \"blob\", \"id\": \"distance_image\" }, { \"type\": \"blob\", \"id\": \"x_image\" }, { \"type\": \"blob\", \"id\": \"y_image\" }, { \"type\": \"blob\", \"id\": \"z_image\" }, { \"type\": \"blob\", \"id\": \"confidence_image\" }, { \"type\": \"blob\", \"id\": \"diagnostic_data\" }, { \"type\": \"string\", \"value\": \"stop\", \"id\": \"end_string\" } ] }"
		answer = self.sendCommand("c%09d%s" % (len(pcicConfig), pcicConfig))
		print(answer)
		if str(answer, 'utf-8') != "*":
			throw
		# enable result output again
		self.sendCommand("p1")

	def readNextFrame(self):
		amplitudeImage = None
		intensityImage = None
		distanceImage = None
		rawAmplitudeImage = None
		xImage = None
		yImage = None
		zImage = None
		confidenceImage = None
		diagnosticData = None
		rawImage = []

		# look for asynchronous output
		ticket, answer = self.readNextAnswer()
		if ticket == b"0000":
			answerIndex = 0

			# read start sequence
			data = answer[answerIndex:answerIndex+4]
			answerIndex += 4
			if self.debugFull == True:
				print('Read 4 Bytes start sequence: "%s"' % data)

			if data != b"star":
				print(data)
				throw

			chunkCounter = 1

			while True:
				# read next 4 bytes
				data = answer[answerIndex:answerIndex+4]
				answerIndex += 4
				
				# stop if frame finished
				if data == b"stop":
					break

				# else read rest of image header
				data += answer[answerIndex:answerIndex+12]
				answerIndex += 12
				if self.debugFull == True:
					print('Read %d Bytes image header: "%r"' % (len(data), data))

				# extract information about chunk
				chunkType, chunkSize, headerSize, headerVersion = struct.unpack('IIII', bytes(data))

				# read rest of chunk header
				data += answer[answerIndex:answerIndex+headerSize-16]
				answerIndex += headerSize-16

				if headerVersion == 1:
					chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, timeStamp, frameCount = struct.unpack('IIIIIIIII', bytes(data))
				else:
					print("Unknown chunk header version %d!" % headerVersion)

				if self.debug == True:
					print('''Data chunk %d:
	Chunk type: %d
	Chunk size: %d
	Header size: %d
	Header version: %d
	Image width: %d
	Image height: %d
	Pixel format: %d
	Time stamp: %d
	Frame counter: %d''' % (chunkCounter, chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, timeStamp, frameCount))

				# read chunk data
				data = answer[answerIndex:answerIndex+chunkSize-headerSize]
				answerIndex += chunkSize-headerSize

				# distinguish pixel type
				if pixelFormat == 0:
					image = array.array('B', data)
				elif pixelFormat == 1:
					image = array.array('b', data)
				elif pixelFormat == 2:
					image = array.array('H', data)
				elif pixelFormat == 3:
					image = array.array('h', data)
				elif pixelFormat == 4:
					image = array.array('I', data)
				elif pixelFormat == 5:
					image = array.array('i', data)
				elif pixelFormat == 6:
					image = array.array('f', data)
				elif pixelFormat == 8:
					image = array.array('d', data)
				else:
					image = None

				# distance image
				if chunkType == 100:
					distanceImage = image

				# amplitude image
				elif chunkType == 101:
					amplitudeImage = image

				# intensity image
				elif chunkType == 102:
					intensityImage = image

				# raw amplitude image
				elif chunkType == 103:
					rawAmplitudeImage = image

				# X image
				elif chunkType == 200:
					xImage = image

				# Y image
				elif chunkType == 201:
					yImage = image

				# Z image
				elif chunkType == 202:
					zImage = image

				# confidence image
				elif chunkType == 300:
					confidenceImage = image

				# raw image
				elif chunkType == 301:
					rawImage.append(data)

				# diagnostic data
				elif chunkType == 302:
					illuTemp, frontendTemp1, frontendTemp2, imx6Temp, evalTime = struct.unpack('=iiiiI', bytes(data))
					diagnosticData = dict([('illuTemp', illuTemp/10.0), ('frontendTemp1', frontendTemp1/10.0), ('frontendTemp2', frontendTemp2/10.0), ('imx6Temp', imx6Temp/10.0), ('evalTime', evalTime)])

				chunkCounter = chunkCounter + 1

		return amplitudeImage, intensityImage, distanceImage, xImage, yImage, zImage, confidenceImage, diagnosticData, rawImage, rawAmplitudeImage
