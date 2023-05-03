#pylightvnc
from server import Server
import logging
import signal

#TODO: multi-thread support
#this server only supports one client at a time

server = Server(display=1)
logger = logging.getLogger('lightvnc')
logger.setLevel(logging.INFO)

loghandler = logging.StreamHandler()
loghandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(name)s] (%(levelname)s) %(message)s')
loghandler.setFormatter(formatter)

logger.addHandler(loghandler)

def sigint_handler(signal, frame):
    logger.info('Received SIGINT, stopping')
    server.stop()

signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    logger.info('Starting VNC server at port %d' % (server.get_port()))
    server.start()