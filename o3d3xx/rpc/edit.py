from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import xmlrpc.client

class Edit:
	def __init__(self, editURL):
		self.url = editURL
		self.rpc = xmlrpc.client.ServerProxy(self.url)
		self.deviceURL = self.url + 'device/'
		self.device = xmlrpc.client.ServerProxy(self.deviceURL)
		self.networkURL = self.deviceURL + 'network/'
		self.network = xmlrpc.client.ServerProxy(self.networkURL)
		self.updateAppUrl()

	def updateAppUrl(self):
		self.applicationURL = self.url + 'application/'
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
