from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import socket
import re

class Client:
    def __init__(self, address, port):
        # open raw socket
        self.pcicSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pcicSocket.connect((address, port))
        self.recvCounter = 0
        self.outFile = None
        self.debug = False
        self.debugFull = False

    def __del__(self):
        self.close()

    def recv(self, numberBytes):
        data = ""
        while len(data) < numberBytes:
            dataPart = self.pcicSocket.recv(numberBytes - len(data))
            data = data + dataPart
        self.recvCounter += numberBytes
        if self.outFile != None:
            self.outFile.write(data)
        return data

    def close(self):
        self.pcicSocket.close()
        
class PCICV3Client(Client):
    def readNextAnswer(self):
        # read PCIC ticket + ticket length
        answer = self.recv(16)
        ticket = answer[0:4]
        answerLength = int(re.findall(r'\d+', answer)[1])
        answer = self.recv(answerLength)
        return ticket, answer[4:-2]

    def readAnswer(self, ticket):
        recvTicket = ""
        answer = ""
        while recvTicket != ticket:
            recvTicket, answer = self.readNextAnswer()
        return answer

    def sendCommand(self, cmd):
        cmdLen = len(cmd) + 6
        lengthHeader = "1000L%09d\r\n" % cmdLen
        self.pcicSocket.sendall(lengthHeader)
        self.pcicSocket.sendall("1000")
        self.pcicSocket.sendall(cmd)
        self.pcicSocket.sendall("\r\n")
        answer = self.readAnswer("1000")
        return answer
