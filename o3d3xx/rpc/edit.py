from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import xmlrpc.client
from .application import *

class Edit:
	def __init__(self, editURL):
		self.url = editURL
		self.rpc = xmlrpc.client.ServerProxy(self.url)
		self.deviceURL = self.url + 'device/'
		self.device = xmlrpc.client.ServerProxy(self.deviceURL)
		self.networkURL = self.deviceURL + 'network/'
		self.network = xmlrpc.client.ServerProxy(self.networkURL)

	def editApplication(self, appIndex):
		self.rpc.editApplication(appIndex)
		self.application = Application(self.url + 'application/')
		return self.application

	def stopEditingApplication(self):
		self.rpc.stopEditingApplication()
		self.application = None

	def __getattr__(self, name):
		# Forward otherwise undefined method calls to XMLRPC proxy
		return getattr(self.rpc, name)
