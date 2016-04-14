from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import xmlrpc.client
from .edit import *

class Session:
	def __init__(self, sessionURL):
		self.url = sessionURL
		self.rpc = xmlrpc.client.ServerProxy(self.url)
		self.rpc.heartbeat(300)

	def setOperatingMode(self, mode):
		if mode == 0:
			self.stopEdit()
		elif mode == 1:
			return self.startEdit()
		else:
			raise ValueError("Invalid operating mode")

	def startEdit(self):
		self.rpc.setOperatingMode(1)
		self.edit = Edit(self.url + 'edit/')
		self.updateAppUrl()
		return self.edit

	def stopEdit(self):
		self.rpc.setOperatingMode(0)
		self.edit = None

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
