import struct

class SecurityType:
    #currently supports 4 security type
    SECTYPES_COUNT = 4
    SECTYPES_INVALID = 0
    SECTYPES_NONE = 1
    SECTYPES_VNCAUTH = 2
    SECTYPES_TIGHT = 16
    SECTYPES_LIST = struct.pack('!BBBBB', SECTYPES_COUNT, 
                                                                      SECTYPES_INVALID,
                                                                      SECTYPES_NONE,
                                                                      SECTYPES_VNCAUTH,
                                                                      SECTYPES_TIGHT)
    SECTYPES_LIST = struct.pack('!BBB', 2, 0, 1)
                                                                      
class SecurityResult:
    OK = struct.pack("!I", 0)
    FAILED = struct.pack('!I', 1)
    NO_ATTEMPTS = struct.pack('!I', 2)

class PixelFormat:
    def __init__(self, bpp=32, depth=24, big_endian=0, true_color=1, red_max=255, green_max=255, blue_max=255, red_shift=16, green_shift=8, blue_shift=0):
        self.bpp = bpp
        self.depth = depth
        self.big_endian = big_endian
        self.true_color = true_color
        self.red_max = red_max
        self.green_max = green_max
        self.blue_max = blue_max
        self.red_shift = red_shift
        self.green_shift = green_shift
        self.blue_shift = blue_shift
        self.padding = struct.pack('!xxx')
        
    def get_bytes(self):
        data = struct.pack('!BBBB', self.bpp, self.depth, self.big_endian, self.true_color)
        data += struct.pack('!HHH', self.red_max, self.green_max, self.blue_max)
        data += struct.pack('!BBB', self.red_shift, self.green_shift, self.blue_shift)
        data += self.padding
        
        return data

class Framebuffer:
    def __init__(self, width=1600, height=720, pixel_format=PixelFormat(), name_length=8, name='lightvnc'):
        self.width = width
        self.height = height
        self.pixel_format = pixel_format
        self.name_length = name_length
        self.name = name

    def get_bytes(self):
        data = struct.pack('!HH', self.width, self.height)
        data += self.pixel_format.get_bytes()
        data += struct.pack('!I', self.name_length)
        data += self.name.encode('utf-8')
        
        return data