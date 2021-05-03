from __future__ import (absolute_import, division, print_function)
from builtins import *
import struct
import array
import json

from o3d3xx.pcic.format_parser import *
from .client import PCICV3Client

class PCICFormatRecord:
    def __init__(self, recordId):
        self.recordMap = {}
        self.recordMap["type"] = "records"
        self.recordMap["id"] = str(recordId)
        self.recordMap["elements"] = []

    def addStringElement(self, id, value):
        stringElement = {}
        stringElement["type"] = "string"
        stringElement["value"] = str(value)
        stringElement["id"] = str(id)
        self.recordMap["elements"].append(stringElement)

    def addBlobElement(self, id):
        blobElement = {}
        blobElement["type"] = "blob"
        blobElement["id"] = str(id)
        self.recordMap["elements"].append(blobElement)

    def toMap(self):
        return self.recordMap

    def toString(self):
        return json.dumps(self.recordMap)

class PCICFormat:
    def __init__(self, formatString=None):
        self.formatMap = {}
        if formatString != None:
            self.formatMap = json.loads(formatString)
        else:
            self.formatMap["layouter"] = "flexible"
            self.formatMap["format"] = { "dataencoding": "ascii" }
            self.formatMap["elements"] = []

    def addStringElement(self, id, value):
        stringElement = {}
        stringElement["type"] = "string"
        stringElement["value"] = str(value)
        stringElement["id"] = str(id)
        self.formatMap["elements"].append(stringElement)

    def addBlobElement(self, id):
        blobElement = {}
        blobElement["type"] = "blob"
        blobElement["id"] = str(id)
        self.formatMap["elements"].append(blobElement)

    def addRecordElement(self, record):
        self.formatMap["elements"].append(record.toMap())

    def toString(self):
        return json.dumps(self.formatMap)

    @staticmethod
    def blobs(*blobIds):
        format = PCICFormat()
        for blobId in blobIds:
            format.addBlobElement(blobId)
        return format

class PCICParser:
    def __init__(self, format=None):
        self.format = format
        self.debug = False

    def extractChunkHeaderInformation(self, answer, answerIndex):
        chunkType, chunkSize, headerSize, headerVersion = struct.unpack('IIII',
                                                                        bytes(answer[answerIndex:answerIndex + 16]))
        # extract full chunk header information
        if headerVersion == 1:
            chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, timeStamp, frameCount = struct.unpack(
                'IIIIIIIII', bytes(answer[answerIndex:answerIndex + headerSize]))
        elif headerVersion == 2:
            chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, timeStamp, frameCount, statusCode, timeStampSec, timeStampNsec = struct.unpack(
                'IIIIIIIIIIII', bytes(answer[answerIndex:answerIndex + headerSize]))
        else:
            print("Unknown chunk header version %d!" % headerVersion)
            return chunkType, chunkSize, None

        if self.debug == True:
            print('''Data chunk:
        	Chunk type: %d
        	Chunk size: %d
        	Header size: %d
        	Header version: %d
        	Image width: %d
        	Image height: %d
        	Pixel format: %d
        	Time stamp: %d
        	Frame counter: %d''' % (
                chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, timeStamp,
                frameCount))

        return chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, timeStamp, frameCount

    def parseBlob(self, answer, answerIndex):
        # extract version independent information from chunk header
        chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, timeStamp, frameCount = self.extractChunkHeaderInformation(answer, answerIndex)

        # check payload size
        if len(answer) < answerIndex + chunkSize:
            raise RuntimeError("data truncated ({} bytes missing)", answerIndex + chunkSize - len(answer))

        # read chunk payload data
        answerIndex += headerSize
        # distinguish pixel type
        if pixelFormat == 0:
            image = array.array('B', bytes(answer[answerIndex:answerIndex + chunkSize - headerSize]))
        elif pixelFormat == 1:
            image = array.array('b', bytes(answer[answerIndex:answerIndex + chunkSize - headerSize]))
        elif pixelFormat == 2:
            image = array.array('H', bytes(answer[answerIndex:answerIndex + chunkSize - headerSize]))
        elif pixelFormat == 3:
            image = array.array('h', bytes(answer[answerIndex:answerIndex + chunkSize - headerSize]))
        elif pixelFormat == 4:
            image = array.array('I', bytes(answer[answerIndex:answerIndex + chunkSize - headerSize]))
        elif pixelFormat == 5:
            image = array.array('i', bytes(answer[answerIndex:answerIndex + chunkSize - headerSize]))
        elif pixelFormat == 6:
            image = array.array('f', bytes(answer[answerIndex:answerIndex + chunkSize - headerSize]))
        elif pixelFormat == 8:
            image = array.array('d', bytes(answer[answerIndex:answerIndex + chunkSize - headerSize]))
        else:
            print("Unknown pixel format %d!" % pixelFormat)
            image = None

        return chunkType, chunkSize, image

    def parseElement(self, answer, answerIndex, element, result):
        if element["type"] == "string":
            readString = answer[answerIndex:answerIndex + len(element["value"])].decode("utf-8")
            if self.debug == True:
                print("String: '{}'".format(readString))
            if readString == element["value"]:
                result[element["id"]] = element["value"]
                return answerIndex + len(element["value"])
            else:
                raise RuntimeError("read result '{}' does not match format (expected '{}')"
                                   .format(readString, element["value"]))
        elif element["type"] == "blob":
            chunkType, chunkSize, blobData = self.parseBlob(answer, answerIndex)
            if element["id"] in result:
                if isinstance(result[element["id"]], list):
                    result[element["id"]].append(blobData)
                else:
                    result[element["id"]] = [result[element["id"]], blobData]
            else:
                result[element["id"]] = blobData
            return answerIndex + chunkSize
        elif element["type"] == "records":
            if self.debug == True:
                print("Record: '{}'".format(element["id"]))
            recordResult, answerIndex = self.parseRecord(answer, answerIndex, element["elements"])
            if element["id"] in result.keys():
                result[element["id"]].append(recordResult[0])
            else:
                result[element["id"]] = recordResult
            return answerIndex
        elif element["type"] in ["int8", "uint8", "int16", "uint16", "int32", "uint32", "float32", "float64"]:
            if self.debug == True:
                print("{}: '{}'".format(element["type"], element["id"]))
            numericResult, answerIndex = self.parseNumeric(answer, answerIndex, element["type"])
            result[element["id"]] = numericResult
            return answerIndex
        raise RuntimeError("cannot handle element type {}".format(element["type"]))

    def parseNumeric(self, answer, answerIndex, elementType):
        numericResult = []
        value = chr(answer[answerIndex])
        while value not in [";", "|", "*"]:
            numericResult += value
            answerIndex += 1
            if not answerIndex == len(answer):
                value = chr(answer[answerIndex])
        # try evaluating an numeric value, else return it as a string
        try:
            if elementType not in ["float32", "float64"]:
                value = int(''.join(numericResult))
            else:
                value = eval(''.join(numericResult))
            return value, answerIndex
        except SyntaxError:
            value = ''.join(numericResult)
            return value, answerIndex

    def parseRecord(self, answer, answerIndex, recordElements):
        recordResult = []
        iterationResult = {}
        for element in recordElements:
            answerIndex = self.parseElement(answer, answerIndex, element, iterationResult)
        recordResult.append(iterationResult)
        return recordResult, answerIndex

    def parseAnswer(self, answer):
        result = {}
        answerIndex = 0
        # print("Parsing answer '%s' against format '%s'" % (answer, self.format.toString()))
        for element in self.format.formatMap["elements"]:
            answerIndex = self.parseElement(answer, answerIndex, element, result)
        return result

class FormatClient(PCICV3Client):
    def __init__(self, address, port, format=None):
        self.format = format
        self.answer = None

        super(FormatClient, self).__init__(address, port)

        ticket, self.answer = self.readNextAnswer()

        # disable all result output
        self.sendCommand("p0")

        # if format is not specified, read back format as configured by the active application
        if not format:
            formatstring = self.sendCommand("C?").decode("utf-8")[9:]
            self.format = PCICFormat(str(formatstring))
        # otherwise set provided format for this connection
        else:
            formatString = self.format.toString()
            answer = self.sendCommand("c%09d%s" % (len(formatString), formatString))
            if str(answer, 'utf-8') != "*":
                raise RuntimeError("could not change PCIC format (format string is '{}')".format(formatString))

        self.parser = PCICParser(self.format)

        # parsing und unrolling the format in case of multiple or nested records
        if not format:
            formatParser = FormatParser(self.parser, self.answer, self.format)
            formatParser.unrolledFormatMap()

        # enable result output again
        self.sendCommand("p1")

    def readNextFrame(self):
        result = {}

        # look for asynchronous output
        ticket, self.answer = self.readNextAnswer()

        if ticket == b"0000":

            self.parser.debug = self.debug
            result = self.parser.parseAnswer(self.answer)
        return result
