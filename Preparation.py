def PrepareChars5x7(jmeno, mezX, mezY):
    im = Image.open(jmeno)
    Pixels = im.load()
    for x in range(13):
        for y in range(4):
            imnew = Image.new(mode="RGB", size=(5, 7))
            pole = imnew.load()
            print(pole[1, 1], imnew.size)
            for x2 in range(5):
                for y2 in range(7):
                    pole[x2, y2] = Pixels[x2 + (5 + mezX) * x, y2 + (7 + mezY) * y]

            imnew.save("Characters/ch" + str(x + 13 * y) + ".png")

def Roztrid():
    from os import listdir, mkdir
    from PIL import Image
    seznam = listdir("Characters")

    for polozka in seznam:
        im = Image.open("Characters/" + polozka)
        pixels = im.load()

        hodnota = 0
        for x in range(5):
            for y in range(7):
                if pixels[x,y][0] != 0:
                    hodnota += 1

        if str(hodnota) not in listdir("Characters"):
            mkdir("Characters/" + str(hodnota))

        im.save("Characters/" + str(hodnota) + "//" + polozka)

