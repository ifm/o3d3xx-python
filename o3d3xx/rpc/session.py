from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import xmlrpc.client

class Session:
	def __init__(self, sessionURL):
		self.sessionURL = sessionURL
		self.rpc = xmlrpc.client.ServerProxy(self.sessionURL)
		self.rpc.heartbeat(300)

	def startEdit(self):
		self.rpc.setOperatingMode(1)
		self.editURL = self.sessionURL + 'edit/'
		self.edit = xmlrpc.client.ServerProxy(self.editURL)
		self.deviceURL = self.editURL + 'device/'
		self.device = xmlrpc.client.ServerProxy(self.deviceURL)
		self.networkURL = self.deviceURL + 'network/'
		self.network = xmlrpc.client.ServerProxy(self.networkURL)
		self.updateAppUrl()

	def updateAppUrl(self):
		self.applicationURL = self.editURL + 'application/'
		self.application = xmlrpc.client.ServerProxy(self.applicationURL)
		self.imagerConfigURL = self.applicationURL + 'imager_001/'
		self.imagerConfig = xmlrpc.client.ServerProxy(self.imagerConfigURL)
		self.spatialFilterURL = self.imagerConfigURL + 'spatialfilter/'
		self.spatialFilter = xmlrpc.client.ServerProxy(self.spatialFilterURL)
		self.temporalFilterURL = self.imagerConfigURL + 'temporalfilter/'
		self.temporalFilter = xmlrpc.client.ServerProxy(self.temporalFilterURL)

	def __getattr__(self, name):
		# Forward otherwise undefined method calls to XMLRPC proxy
		return getattr(self.rpc, name)
