#raw encoding

import struct
from PIL import Image

class RawEncoding:
    
    #gets the value for FramebufferUpdate command
    def framebufferupdate_get(x, y, w, h, pixel):
        ENCODING_NUMBER = 0
        RECT=1
        data = bytearray()
        data.extend(struct.pack('!BxH', 0, RECT))
        data.extend(struct.pack('!HHHH', x, y, w, h))
        data.extend(struct.pack('!i', ENCODING_NUMBER))
        data.extend(pixel.tobytes())
        
        return data