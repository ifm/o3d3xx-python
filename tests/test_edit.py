from unittest import TestCase

import o3d3xx
from .config import *

class TestEdit(TestCase):
	def setUp(self):
		self.device = o3d3xx.Device(deviceAddress)
		self.session = self.device.requestSession()
		self.edit = self.session.startEdit()

	def tearDown(self):
		self.session.stopEdit()
		self.session.cancelSession()

	def test_edit_proxies(self):
		result = self.edit.device.getAllParameters()
		self.assertIsInstance(result, dict)
		result = self.edit.network.getAllParameters()
		self.assertIsInstance(result, dict)

	def test_create_delete_application(self):
		appIndex = self.edit.createApplication()
		self.edit.deleteApplication(appIndex)

	def test_edit_application(self):
		appIndex = self.edit.createApplication()
		self.edit.editApplication(appIndex)
		result = self.edit.application.getAllParameters()
		self.assertIsInstance(result, dict)
		print self.edit.application.imagerConfig
		result = self.edit.application.imagerConfig.getAllParameters()
		self.assertIsInstance(result, dict)
		result = self.edit.application.spatialFilter.getAllParameters()
		self.assertIsInstance(result, dict)
		result = self.edit.application.temporalFilter.getAllParameters()
		self.assertIsInstance(result, dict)
		self.edit.stopEditingApplication()
		self.edit.deleteApplication(appIndex)
