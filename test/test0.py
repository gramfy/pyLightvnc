from PIL import Image

img = Image.open('images.png')
data = bytearray()
data = img.tobytes()

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

r = clamp(data[0], 0, 255)
g = clamp(data[1], 0, 255)
b = clamp(data[2], 0, 255)
a = clamp(data[3], 0, 255)

rgba = (r << 24) | (g << 16) | (b << 8) | (a << 0)
print(hex(g))

print(len(data))