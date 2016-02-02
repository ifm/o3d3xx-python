from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import xmlrpc.client
from .session import *

class Device:
    def __init__(self, address):
        self.address = address
        self.baseURL = 'http://'+address+'/api/rpc/v1/'
        self.mainURL = self.baseURL + 'com.ifm.efector/'
        self.rpc = xmlrpc.client.ServerProxy(self.mainURL)

    def createSession(self, password=""):
        self.sessionID = self.rpc.requestSession(password, "")
        self.sessionURL = self.mainURL + 'session_' + self.sessionID + '/'
        self.session = Session(self.sessionURL)
        return self.session

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)
