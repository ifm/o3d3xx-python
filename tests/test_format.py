from unittest import TestCase

import array
from o3d3xx.pcic.format_client import *

amplitudeImageBlob = bytes.fromhex("67000000340000003000000002000000020000000100000002000000000000000100000000000000000000000000000001000200")
distanceImageBlob = bytes.fromhex("64000000340000003000000002000000020000000100000002000000000000000100000000000000000000000000000003000400")
truncatedImageBlob = bytes.fromhex("670000003400000030000000020000000200000001000000020000000000000001000000000000000000000000000000")

class TestPcicParser(TestCase):
    def test_string(self):
        format = PCICFormat()
        format.addStringElement("key", "value")
        parser = PCICParser(format)

        result = parser.parseAnswer(b"value")
        self.assertDictEqual(result, {"key": "value"})

        with self.assertRaises(RuntimeError) as cm:
            result = parser.parseAnswer(b"wrong")

    def test_blob(self):
        format = PCICFormat()
        format.addBlobElement("amplitude_image")
        parser = PCICParser(format)

        result = parser.parseAnswer(amplitudeImageBlob)
        self.assertDictEqual(result, {"amplitude_image": array.array('H', [1, 2])})

        with self.assertRaises(RuntimeError) as cm:
            result = parser.parseAnswer(truncatedImageBlob)

    def test_blob_sequence(self):
        format = PCICFormat()
        format.addBlobElement("amplitude_image")
        format.addBlobElement("distance_image")
        parser = PCICParser(format)

        result = parser.parseAnswer(amplitudeImageBlob + distanceImageBlob)
        self.assertDictEqual(result, {
                "amplitude_image": array.array('H', [1, 2]),
                "distance_image": array.array('H', [3, 4])
            })

    def test_records(self):
        images = PCICFormatRecord("images")
        images.addBlobElement("amplitude_image")
        format = PCICFormat()
        format.addRecordElement(images)
        format.addRecordElement(images)
        parser = PCICParser(format)

        result = parser.parseAnswer(amplitudeImageBlob + amplitudeImageBlob)
        self.assertDictEqual(result,
            {"images": [
                {"amplitude_image": array.array('H', [1, 2])},
                {"amplitude_image": array.array('H', [1, 2])}
            ]}
        )

    def test_formatParser(self):
        with open('./data/answer.txt', 'r') as file:
            string_answer = file.read()
            encoded_string = string_answer.encode()
            answer = bytearray(encoded_string)
        with open('./data/formatString.txt', 'r') as file:
            formatstring = file.read()

        format = PCICFormat(str(formatstring))
        parser = PCICParser(format)
        format_parser = FormatParser(parser, answer, format)
        format_unrolled = format_parser.unrolledFormatMap()

        with open('./data/formatStringReference.txt', 'r') as file:
            formatstring = file.read()

        format_reference = PCICFormat(str(formatstring))
        self.assertDictEqual(format_unrolled.formatMap, format_reference.formatMap)

    def test_parseAnswer(self):
        with open('./data/answer.txt', 'r') as file:
            string_answer = file.read()
            encoded_string = string_answer.encode()
            answer = bytearray(encoded_string)
        with open('./data/formatString.txt', 'r') as file:
            formatstring = file.read()

        format = PCICFormat(str(formatstring))
        parser = PCICParser(format)
        format_parser = FormatParser(parser, answer, format)
        format_parser.unrolledFormatMap()

        result = parser.parseAnswer(answer)

        self.assertEqual(result['models'].__len__(), 2)
        self.assertEqual(result['models'][0]['rois'].__len__(), 3)
        self.assertEqual(result['models'][1]['rois'].__len__(), 3)

        self.assertEqual(result['models'][0]['rois'][0]['state'], 6)
        self.assertEqual(result['models'][0]['rois'][1]['state'], 6)
        self.assertEqual(result['models'][0]['rois'][2]['state'], 0)
        self.assertEqual(result['models'][0]['rois'][0]['procval'], 0.607)
        self.assertEqual(result['models'][0]['rois'][1]['procval'], 0.532)
        self.assertEqual(result['models'][0]['rois'][2]['procval'], 0.446)
        self.assertEqual(result['models'][0]['rois'][0]['id'], 0)
        self.assertEqual(result['models'][0]['rois'][1]['id'], 1)
        self.assertEqual(result['models'][0]['rois'][2]['id'], 2)

        self.assertEqual(result['models'][1]['rois'][0]['state'], 6)
        self.assertEqual(result['models'][1]['rois'][1]['state'], 6)
        self.assertEqual(result['models'][1]['rois'][2]['state'], 0)
        self.assertEqual(result['models'][1]['rois'][0]['procval'], 0.567)
        self.assertEqual(result['models'][1]['rois'][1]['procval'], 0.601)
        self.assertEqual(result['models'][1]['rois'][2]['procval'], 0.5)
        self.assertEqual(result['models'][1]['rois'][0]['id'], 0)
        self.assertEqual(result['models'][1]['rois'][1]['id'], 1)
        self.assertEqual(result['models'][1]['rois'][2]['id'], 2)
