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
        parser = PCICParser(format)

        result = parser.parseAnswer(amplitudeImageBlob + amplitudeImageBlob)
        self.assertDictEqual(result,
            {"images": [
                {"amplitude_image": array.array('H', [1, 2])},
                {"amplitude_image": array.array('H', [1, 2])}
            ]}
        )
