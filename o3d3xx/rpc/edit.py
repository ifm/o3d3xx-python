from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import xmlrpc.client

class Edit:
	def __init__(self, editURL):
		self.url = editURL
		self.rpc = xmlrpc.client.ServerProxy(self.url)
		self.deviceURL = self.url + 'device/'
		self.device = xmlrpc.client.ServerProxy(self.deviceURL)
		self.networkURL = self.url + 'network/'
		self.network = xmlrpc.client.ServerProxy(self.networkURL)

	def __getattr__(self, name):
		# Forward otherwise undefined method calls to XMLRPC proxy
		return getattr(self.rpc, name)
