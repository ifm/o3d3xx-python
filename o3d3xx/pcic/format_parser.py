import copy
import re

class FormatParser:
    def __init__(self, pcicParser, answer=None, format=None):
        self.pcicParser = pcicParser
        self.answer = answer
        self.format = format

        self.parentChildDelimiter = None

        self.nativeFormat = copy.deepcopy(self.format)

        # Parse all parent and child delimiter if no attribute is empty
        self.parentChildDelimiter = self.parseParentChildDelimiter(answer)

        # self.evaluateParentChildDelimiter(answer)
        # self.appendContentToFormatMap("parentChildDelimiter", self.parentChildDelimiter)

        # Unrolling whole formatMap so you can parse nested records
        # self.unrolledFormatMap()

    # def appendContentToFormatMap(self, key, value):
    #     if "runtime" in self.format.formatMap.keys():
    #         self.format.formatMap["runtime"].update({key: value})
    #     else:
    #         self.format.formatMap["runtime"] = {key: value}

    @property
    def formatMapRecord(self):
        """
        Returns a copy of the next found records element in format map
        :return:
        """
        for i, element in enumerate(self.nativeFormat.formatMap["elements"]):
            if element["type"] == "records":
                return copy.deepcopy(self.nativeFormat.formatMap["elements"][i])

    @property
    def recordIndex(self):
        """
        Returns the next record index in format map
        :return: index as int
        """
        for i, element in enumerate(self.nativeFormat.formatMap["elements"]):
            if element["type"] == "records":
                return i

    def unrolledFormatMap(self):
        """
        Unrolling whole formatMap
        :return: unrolled format map
        """
        def unrollChildRecords(delimiter):
            record = self.formatMapRecord
            for i, element in enumerate(record["elements"]):
                if element["type"] == "records":
                    # childElement = record["elements"][i]
                    amount = len(delimiter["childDelimiterIdx"])
                    [record["elements"].insert(i + 1, record["elements"][i]) for _ in range(amount - 1)]
                    break
            return record

        # Populate record elements with help of parent and child delimiter
        if self.parentChildDelimiter:
            unrolledRecords = [unrollChildRecords(delimiter) for delimiter in self.parentChildDelimiter]

            # Delete old record element from formatMap
            del (self.format.formatMap["elements"][self.recordIndex])
            # Insert populated records in formatMap
            for rec in reversed(unrolledRecords):
                self.format.formatMap["elements"].insert(self.recordIndex, rec)

        return self.format

    def _parseBlobRanges(self, answer):
        """
        Parsing the blob positions in answer from front and reversed order
        :param answer: answer as bytearray
        :return: indices which declare the positions of the blobs
        """
        blobRanges = []
        answerIndex = 0
        recordsStartIndex = 0
        blobIndices = [i for i, elem in enumerate(self.format.formatMap["elements"]) if elem["type"] == "blob"]
        recordsIndices = [i for i, elem in enumerate(self.format.formatMap["elements"]) if
                          elem["type"] == "records"]
        if blobIndices:
            blobAheadRecords = any([blobIndices < recordsIndices])
            blobAfterRecords = any([sorted(blobIndices, key=int, reverse=True) > recordsIndices])
            if blobAheadRecords:
                for element in self.format.formatMap["elements"]:
                    elementType = element["type"]
                    if elementType == "blob":
                        chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, \
                        timeStamp, frameCount = self.pcicParser.extractChunkHeaderInformation(answer, answerIndex)
                        blobRanges.append([answerIndex, answerIndex + chunkSize])
                        answerIndex += chunkSize
                    elif elementType == "records":
                        recordsStartIndex = answerIndex
                        break
                    else:
                        answerIndex = self.pcicParser.parseElement(answer, answerIndex, element, {})

            if blobAfterRecords and blobAheadRecords and recordsIndices:
                blobElementAfterRecords = int(len(answer) / chunkSize) - len(blobRanges)
                blobElementAfterRecordsModulo = int(len(answer) % chunkSize)
                answerAheadBlob = [0, blobElementAfterRecordsModulo - blobElementAfterRecords - len("stop") - 1]
                blobRanges.append([recordsStartIndex + answerAheadBlob[1], len(answer)])

            if blobAfterRecords and not blobAheadRecords and not recordsIndices:
                for element in self.format.formatMap["elements"]:
                    elementType = element["type"]
                    if elementType == "blob":
                        chunkType, chunkSize, headerSize, headerVersion, imageWidth, imageHeight, pixelFormat, \
                        timeStamp, frameCount = self.pcicParser.extractChunkHeaderInformation(answer, answerIndex)
                        blobRanges.append([answerIndex, answerIndex + chunkSize])
                        answerIndex += chunkSize
                    else:
                        answerIndex = self.pcicParser.parseElement(answer, answerIndex, element, {})

            if blobAfterRecords and not blobAheadRecords and recordsIndices:
                raise NotImplementedError("It is not possible to parse blob elements at the end of the bytearray "
                                          "answer. You can place two blob elements between or ahead your records.")

        # TODO push content to meta dict
        self.metaDict = 0
        # self.appendContentToFormatMap("image_resolution", {"imageWidth": imageWidth, "imageHeight": imageHeight})
        # self.appendContentToFormatMap("chunk_size", chunkSize)
        return blobRanges, recordsStartIndex

    def parseParentChildDelimiter(self, answer):
        """
        Parsing parent and child delimiter in answer
        :param answer: answer as bytearray
        :return: list
        """
        parentChildDelimiter = []
        blobRanges, delimiterIndex = self._parseBlobRanges(answer)
        parentDelimiter = [delimiter for delimiter in re.finditer(b"\|", answer)
                           if not any(True for blob in blobRanges if blob[0] <= delimiter.span()[0] <= blob[1])]

        if parentDelimiter:
            for i, delimiter in enumerate(parentDelimiter):
                childDelimiter = [m for m in re.finditer(b"\*", answer[delimiterIndex: delimiter.span()[0]])]
                parentChildDelimiter.append({"parentDelimiterIdx": delimiter.span()[0],
                                             "childDelimiterIdx": [d.span()[0] + delimiterIndex for d in
                                                                   childDelimiter],
                                             "parentDelimiter": "|", "childDelimiter": "*"})
                delimiterIndex = delimiter.span()[0]
            return parentChildDelimiter
