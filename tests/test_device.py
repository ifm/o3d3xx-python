from unittest import TestCase

import o3d3xx
import xmlrpc
from .config import *

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

	def test_double_session(self):
		session = self.device.requestSession()
		with self.assertRaises(xmlrpc.client.Fault) as cm:
			session2 = self.device.requestSession()
		self.assertEqual(cm.exception.faultCode, 101004)
		session.cancelSession()
