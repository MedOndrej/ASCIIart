from PIL import Image
import math

def Grayscale(path):
    im = Image.open(path)
    Pixels = im.load()
    width, height = im.size

    for x in range(width):
        for y in range(height):
            mono = (0.2125 * Pixels[x, y][0]) + (0.7154 * Pixels[x, y][1]) + (0.0721 * Pixels[x, y][2])
            mono = math.floor(mono)
            Pixels[x, y] = (mono, mono, mono)

    im.save("G" + path)
    return "G" + path

def Onebit(path):
    im = Image.open(path)
    Pixels = im.load()
    width, height = im.size

    for x in range(width):
        for y in range(height):
            mono = (0.2125 * Pixels[x,y][0]) + (0.7154 * Pixels[x,y][1]) + (0.0721 * Pixels[x,y][2])
            if mono >= 128:
                mono = 255
            else:
                mono = 0
            Pixels[x,y] = (mono,mono,mono)

    im.save("1" + path)
    return "1" + path