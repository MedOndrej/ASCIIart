from PIL import Image
from os import listdir
import math

def Grayscale(path):
    im = Image.open(path)
    Pixels = im.load()
    width, height = im.size

    for x in range(width):
        for y in range(height):
            mono = (0.2125 * Pixels[x,y][0]) + (0.7154 * Pixels[x,y][1]) + (0.0721 * Pixels[x,y][2])
            mono = math.floor(mono)
            Pixels[x,y] = (mono,mono,mono)

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

def FixResolution(pathORG, pathFIN, WID, HEI):
    im = Image.open(pathORG)
    pixels = im.load()

    width, height = im.size

    widthX = (WID - width % WID) % WID
    heightX = (HEI - height % HEI) % HEI

    widthTB = width + widthX
    heightTB = height + heightX
    print(widthTB, heightTB)

    imN = Image.new("RGB", (widthTB, heightTB))
    pixelsN = imN.load()

    for x in range(width):
        for y in range(heightTB):
            if y < heightX // 2:
                pixelsN[widthX // 2 + x, y] = pixels[x, 0]
            elif y > heightX // 2 + height - 5:
                pixelsN[widthX // 2 + x, y] = pixels[x, height - 1]
            else:
                pixelsN[widthX // 2 + x, y] = pixels[x, y]

    for y in range(heightTB):
        for x in range(widthX):
            if x < widthX // 2:
                pixelsN[x, y] = pixelsN[widthX // 2 + x, y]
            else:
                pixelsN[widthTB - (widthX - x), y] = pixelsN[width + widthX // 2 - 1, y]

    imN.save(pathFIN)

def CalculateValues(path, WID, HEI):
    im = Image.open(path)
    Pixels = im.load()
    width, height = im.size
    widthS, heightS = width // WID, height // HEI
    Values = [[0 for y in range(heightS + 2)] for x in range(widthS + 2)]

    for x in range(width):
        for y in range(height):
            Values[x // WID + 1][y // HEI + 1] += (0.2125 * Pixels[x,y][0]) + (0.7154 * Pixels[x,y][1]) + (0.0721 * Pixels[x,y][2])

    for x in range(widthS):
        for y in range(heightS):
            Values[x + 1][y + 1] /= (WID * HEI)

    return Values

def GetTones():

    list = listdir("Characters/Sorted")

    for x in range(len(list)):
        list[x] = int(list[x])

    return list

def FindFit(ToneToFit, Tones):
    Tones = sorted(Tones)
    if ToneToFit <= 0:
        return 0
    elif ToneToFit >= 255:
        return 35

    ToneToFit *= 35 / 255

    fit = 0

    #potenciální zrychlení binárním vyhledáváním
    for x in range(len(Tones)):
        if Tones[x] > ToneToFit:
            fit = x
            break

    if ToneToFit - Tones[fit - 1] <= Tones[fit] - ToneToFit:
        return Tones[fit - 1]
    return Tones[fit]

def PickCharacter(Tone):
    items = listdir("Characters/Sorted/" + str(Tone))

    return items[0]

def GenerateASCII(path, WID, HEI):
    FixResolution(path, path, WID, HEI)
    Values = CalculateValues(path, WID, HEI)
    Tones = GetTones()

    im = Image.open(path)
    BLANK = Image.new("RGB", im.size, (255, 255, 255))
    Pixels = BLANK.load()
    width, height = im.size
    widthS = width // WID
    heightS = height // HEI


    coeff = [255 / 37, 7 / 16, 1 / 16, 5 / 16, 3 / 16]
    for xS in range(widthS):
        for yS in range(heightS):
            fit = FindFit(Values[xS + 1][yS + 1], Tones)
            Values[xS + 2][yS + 1] += coeff[1] * (Values[xS + 1][yS + 1] - fit * (coeff[0]))
            Values[xS + 2][yS + 2] += coeff[2] * (Values[xS + 1][yS + 1] - fit * (coeff[0]))
            Values[xS + 1][yS + 2] += coeff[3] * (Values[xS + 1][yS + 1] - fit * (coeff[0]))
            Values[xS + 0][yS + 2] += coeff[4] * (Values[xS + 1][yS + 1] - fit * (coeff[0]))

            character = Image.open("Characters/Sorted/" + str(fit) + "//" + PickCharacter(fit))

            PixelsCH = character.load()

            for x in range(WID - 2):
                for y in range(HEI - 2):
                    Pixels[xS * WID + x + 1, yS * HEI + y + 1] = PixelsCH[x, y]

    BLANK.save(path[0:-4] + "3" + path[-4:])


path = "Tests/Raw"
tests = listdir(path)

for test in tests:
    #FixResolution(path + "\\" + test, path + "\\FIXED" + test , 7, 9)
    GenerateASCII(path + "\\" + test, 7, 9)




