from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import xmlrpc.client

class Application:
	def __init__(self, applicationURL):
		self.url = applicationURL
		self.rpc = xmlrpc.client.ServerProxy(self.url)
		self.imagerConfigURL = self.url + 'imager_001/'
		self.imagerConfig = xmlrpc.client.ServerProxy(self.imagerConfigURL)
		self.spatialFilterURL = self.imagerConfigURL + 'spatialfilter/'
		self.spatialFilter = xmlrpc.client.ServerProxy(self.spatialFilterURL)
		self.temporalFilterURL = self.imagerConfigURL + 'temporalfilter/'
		self.temporalFilter = xmlrpc.client.ServerProxy(self.temporalFilterURL)

	def __getattr__(self, name):
		# Forward otherwise undefined method calls to XMLRPC proxy
		return getattr(self.rpc, name)
