import socket
import logging
import struct

from PIL import Image
from protocol import SecurityType
from protocol import Framebuffer
from auth import NoneAuth
from auth import VNCAuth
from lib_encodings.encoding_raw import RawEncoding

logger = logging.getLogger('lightvnc')

class Server:
    def __init__(self, port=5900, display=0, address='', password=b'\x01\x02\x03\x04\x05\x06\x07\x08'):
        self.port = port + display #default at :1 (5900)
        self.address = address
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.running = True
        self.client = 0
        self.password = password
        self.client_address = 0
        self.rfb_version = b'RFB 003.008\n' #currently the only version supported, do not change
        self.client_rfb_version = 0
        self.client_security = 1
        self.shared_desktop = 0
        self.client_encoding = 0
        self.framebuffer = Framebuffer ()
        self.image = Image.open('Out.jpg').convert('RGBA')
        self.configure_socket()
        
    def configure_socket(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.address, self.port))
        self.socket.listen(5)
        
    def get_port(self):
        return self.port
        
    def stop(self):
        self.running = False
        self.socket.close()
        
    #safe recv (with timeout)
    def recv_safe(self, socket, size):
        socket.settimeout(5)
        
        try:
            data = socket.recv(size)
        except TimeoutError:
            logger.debug('TimeoutError exception during recv_safe')
            data = 0
        socket.settimeout(None)
        return data
    
    def do_handshake_and_auth(self):
        self.client, self.client_address = self.socket.accept()
        logger.info('Incoming connection, establishing handshake')
        logger.info('ProtocolVersion: Using protocol version 3.8')
        self.client.send(self.rfb_version)
        self.client_rfb_version = self.client.recv(12)
        if self.client_rfb_version != self.rfb_version:
            logger.info('Client RFB version (%s) does not match with server RFB version (%s), not accepted.' % (self.client_rfb_version.decode().replace('\n', ''), self.rfb_version.decode().replace('\n', '')))
            self.client.close()
            self.do_handshake()
        self.client.send(SecurityType.SECTYPES_LIST)
        self.client_security = self.client.recv(1)
        logger.debug('Client using security type number %d' % (int.from_bytes(self.client_security, 'big')))
        #do authentication, and initialisation message
        if self.client_security == b'\x01': #none
            NoneAuth(self.socket, self.client).do_auth()
        elif self.client_security == b'\x02': #vncauth
            VNCAuth(self.socket, self.client, self.password).do_auth()
        else:
            logger.error('Unsupported security type.')
        
        
        #unsure results from previous testing, use recv_safe
        self.shared_desktop = self.recv_safe(self.client, 1)
        logger.debug('Shared desktop: %d' % (int.from_bytes(self.shared_desktop, 'big')))
        #send framebuffer and pixelformat info
        logger.debug('Framebuffer data size: %d' % (len(self.framebuffer.get_bytes())))
        self.client.send(self.framebuffer.get_bytes())
        
    def start(self):
        self.do_handshake_and_auth()
        while self.running:
            try:
                cmd=self.client.recv(1)
            except Exception:
                cmd=None
            
            if cmd == b'\x00':
                data = self.client.recv(19)
                if len(data) == 19:
                    (bpp,depth,big_endian,true_color,red_max,green_max,blue_max,red_shift,green_shift,blue_shift) = struct.unpack('!xxxBBBBHHHBBBxxx', data)
                    logger.debug('SetPixelFormats')
                    logger.debug('BPP: %d' % bpp)
                    logger.debug('Big endian: %d' % big_endian)
                    logger.debug('True color: %d' % true_color)
                    logger.debug('Red max: %d, green max: %d, blue max: %d' % (red_max,green_max,blue_max))
                    logger.debug('Red shift: %d, green shift: %d, blue shift: %d' % (red_shift, green_shift,blue_shift))
            if cmd == b'\x02':
                data = self.client.recv(3)
                (data,) = struct.unpack('!xH', data)
                self.client_encoding = struct.unpack('!%si' % data, self.client.recv(4 * data))
                logger.debug('SetEncodings')
            if cmd == b'\x03':
                data = self.client.recv(9)
                if len(data) == 9:
                    logger.debug('FramebufferUpdateRequest')
                    (inc, x, y, w, h) = struct.unpack('!BHHHH', data)
                    image = self.image.crop((x, y, w, h))
                    self.client.send(RawEncoding.framebufferupdate_get(x,y,w,h,image))
            if cmd == b'\x04':
                self.client.recv(7)
                logger.debug('KeyEvent')
            if cmd == b'\x05':
                self.client.recv(5)
                logger.debug('PointerEvent')