from unittest import TestCase

import o3d3xx
from .config import *

class TestSession(TestCase):
	def setUp(self):
		print("Create session")
		self.device = o3d3xx.Device(deviceAddress)
		self.session = self.device.requestSession()

	def tearDown(self):
		self.session.cancelSession()

	def test_heartbeat(self):
		result = self.session.heartbeat(300)
		self.assertEqual(result, 300)

	def test_start_stop_edit(self):
		self.session.startEdit()
		self.session.stopEdit()
