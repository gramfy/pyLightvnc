from protocol import SecurityResult
import os
import socket
import logging
import pyDes

logger = logging.getLogger('lightvnc')

class NoneAuth:
    def __init__(self, socket, client):
        self.socket = socket
        self.client = client

    def do_auth(self):
        logger.debug('Authenticating with None')
        self.client.send(SecurityResult.OK)

class VNCAuth:
    def __init__(self, socket, client, password):
        self.socket = socket
        self.client = client
        self.password = password

    def do_auth(self):
        logger.debug('Authenticating with VNCAuth')
        challange = os.urandom(16)
        self.client.send(challange)
        response = self.client.recv(16)
        
        #for now we'll force OK
        self.client.send(SecurityResult.OK)
        