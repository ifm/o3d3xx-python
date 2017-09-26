from __future__ import (absolute_import, division, print_function)
from builtins import *
import struct
import array
import json

from .client import PCICV3Client

class ImageClient(PCICV3Client):

    def setDataRequests(self, normAmpl = True, dist=True, x = True, y = True, z = True, conf = True, diag = True, models = True
                                ):
        pcicConfig = ("{"
            "\"layouter\": \"flexible\","
            "\"format\": { \"dataencoding\": \"ascii\" },"
            "\"elements\": [")
            
        pcicConfig = pcicConfig + "{ \"type\": \"string\", \"value\": \"star\", \"id\": \"start_string\" },"
                
        if normAmpl is True:
            pcicConfig = pcicConfig + "{ \"type\": \"blob\", \"id\": \"normalized_amplitude_image\" },"
        if dist is True:
            pcicConfig = pcicConfig + "{ \"type\": \"blob\", \"id\": \"distance_image\" },"
        if x is True:
            pcicConfig = pcicConfig + "{ \"type\": \"blob\", \"id\": \"x_image\" },"
        if y is True:
            pcicConfig = pcicConfig + "{ \"type\": \"blob\", \"id\": \"y_image\" },"
        if z is True:
            pcicConfig = pcicConfig + "{ \"type\": \"blob\", \"id\": \"z_image\" },"
        if conf is True:
            pcicConfig = pcicConfig + "{ \"type\": \"blob\", \"id\": \"confidence_image\" },"
        if diag is True:
            pcicConfig = pcicConfig + "{ \"type\": \"blob\", \"id\": \"diagnostic_data\" },"
        if models is True:
            pcicConfig = pcicConfig + "{ \"type\": \"blob\", \"id\": \"json_model\"},"
        
        pcicConfig = pcicConfig + "{ \"type\": \"string\", \"value\": \"stop\", \"id\": \"end_string\" } ] }"
        
        self.sendCommand("p0")
        # format string for requesting data
        answer = self.sendCommand("c%09d%s" % (len(pcicConfig), pcicConfig))
        if str(answer, 'utf-8') != "*":
            throw
        # enable result output again
        self.sendCommand("p1")
        
    def __init__(self, address, port):
        super(ImageClient, self).__init__(address, port)
        # disable all result output
        self.setDataRequests(True, True, True, True, True, True, True)
        
    def readNextFrame(self):
        result = {}
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
                elif headerVersion == 2:
                    chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, timeStamp, frameCount, statusCode, timeStampSec, timeStampNsec = struct.unpack('IIIIIIIIIIII', bytes(data))
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
                    image = array.array('B', bytes(data))
                elif pixelFormat == 1:
                    image = array.array('b', bytes(data))
                elif pixelFormat == 2:
                    image = array.array('H', bytes(data))
                elif pixelFormat == 3:
                    image = array.array('h', bytes(data))
                elif pixelFormat == 4:
                    image = array.array('I', bytes(data))
                elif pixelFormat == 5:
                    image = array.array('i', bytes(data))
                elif pixelFormat == 6:
                    image = array.array('f', bytes(data))
                elif pixelFormat == 8:
                    image = array.array('d', bytes(data))
                else:
                    image = None

                # distance image
                if chunkType == 100:
                    result['distance'] = image

                # amplitude image
                elif chunkType == 101:
                    result['amplitude'] = image

                # intensity image
                elif chunkType == 102:
                    result['intensity'] = image

                # raw amplitude image
                elif chunkType == 103:
                    result['rawAmplitude'] = image

                # X image
                elif chunkType == 200:
                    result['x'] = image

                # Y image
                elif chunkType == 201:
                    result['y'] = image

                # Z image
                elif chunkType == 202:
                    result['z'] = image

                # confidence image
                elif chunkType == 300:
                    result['confidence'] = image

                # raw image
                elif chunkType == 301:
                    if 'raw' not in result:
                        result['raw'] = []
                    result['raw'].append(image)

                # diagnostic data
                elif chunkType == 302:
                    illuTemp, frontendTemp1, frontendTemp2, imx6Temp, evalTime = struct.unpack('=iiiiI', bytes(data))
                    diagnosticData = dict([('illuTemp', illuTemp/10.0), ('frontendTemp1', frontendTemp1/10.0), ('frontendTemp2', frontendTemp2/10.0), ('imx6Temp', imx6Temp/10.0), ('evalTime', evalTime)])
                    result['diagnostic'] = diagnosticData

                elif chunkType == 500:
                    if 'models' not in result:
                            result['models'] = [];
                    result['models'] = json.loads(data)
                chunkCounter = chunkCounter + 1

        # return amplitudeImage, intensityImage, distanceImage, xImage, yImage, zImage, confidenceImage, diagnosticData, rawImage, rawAmplitudeImage
        return result
