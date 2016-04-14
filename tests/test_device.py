from unittest import TestCase

import o3d3xx

deviceAddress = '172.25.125.100'

class TestDevice(TestCase):
	def setUp(self):
		self.device = o3d3xx.Device(deviceAddress)

	def test_get_sw_version(self):
		result = self.device.getSWVersion()
		self.assertIsInstance(result, dict)

	def test_request_session(self):
		session = self.device.requestSession()
		self.assertIsInstance(session, o3d3xx.Session)
		session.cancelSession()
