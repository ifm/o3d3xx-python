from unittest import TestCase

import o3d3xx
from .config import *

class TestPcic(TestCase):
	def setUp(self):
		self.pcic = o3d3xx.PCICV3Client(deviceAddress, 50010)

	def test_pcic_version(self):
		result = self.pcic.sendCommand("V?")
		self.assertEqual(result, b"03 01 04")
