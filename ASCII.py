from PIL import Image
from os import listdir, path
from random import randint

class ASCII():
    def __init__(self, path, fore, back):
        """
        :param path: stored in self.path
        :param fore:           self.fore
        :param back:           self.back

        self.path           stores address of the image
        self.im             stores an instance of the Image class of PIL library
        self.pixels         is an access to the image's pixels
        self.width/height   dimensions of the image
        self.wid/hei_area   dimensions of an area that is represented by a single character
        self.char_area      Area over which a character is painted (excluding margin)
        self.fore/back      RGB values of background and characters
        self.tones          list of available Tones in "Character Bank"
        self.tonesLength    number of different Tones
        self.char_arrays    list interpretation of characters in use
        self.tone_counts    number of characters for each tone, i.e. number of pixels a character (of given tone)
                            takes up
        """
        self.path = path
        self.im = Image.open(self.path)
        self.pixels = self.im.load()
        self.width, self.height = self.im.size
        self.wid_area = 7
        self.hei_area = 9
        self.char_area = (self.wid_area - 2) * (self.hei_area - 2)
        self.fore = fore
        self.back = back
        self.tones = self.GetTones()
        self.tonesLength = len(self.tones)
        self.char_arrays = self.GenerateCharArrays()
        self.tone_counts = self.CountTones()

    def FixResolution(self):
        """
        Replaces self.im, self.pixels by enlarged variant with dimensions divisible by self.wid/hei_area. To do so
        outer pixel rows are copied.
        """
        widthX = (self.wid_area - self.width % self.wid_area) % self.wid_area
        heightX = (self.hei_area - self.height % self.hei_area) % self.hei_area

        widthTB = self.width + widthX
        heightTB = self.height + heightX

        im = Image.new("RGB", (widthTB, heightTB))
        pixels = im.load()

        for x in range(self.width):
            for y in range(heightTB):
                if y < heightX // 2:
                    pixels[widthX // 2 + x, y] = self.pixels[x, 0]
                elif y > heightX // 2 + self.height - 5:
                    pixels[widthX // 2 + x, y] = self.pixels[x, self.height - 1]
                else:
                    pixels[widthX // 2 + x, y] = self.pixels[x, y]

        for y in range(heightTB):
            for x in range(widthX):
                if x < widthX // 2:
                    pixels[x, y] = pixels[widthX // 2 + x, y]
                else:
                    pixels[widthTB - (widthX - x), y] = pixels[self.width + widthX // 2 - 1, y]

        self.im = im
        self.pixels = pixels

    def CalculateValues(self):
        """
        :return: Returns the average grayscale tone of each area to be occupied by a specific letter, stored in an array
        Values[x axis][y axis], where final item is average tone.
        Uses coefficients 0.2125, 0.7154, 0.0721 for red, green and blue respectively.
        """
        x_areas = self.width // self.wid_area
        y_areas = self.height // self.hei_area

        values = [[0 for y in range(y_areas + 2)] for x in range(x_areas + 2)]

        for x in range(self.width):
            for y in range(self.height):
                values[x // self.wid_area + 1][y // self.hei_area + 1] += (0.2125 * self.pixels[x,y][0]) + \
                                                                          (0.7154 * self.pixels[x,y][1]) + \
                                                                          (0.0721 * self.pixels[x,y][2])

        cumulative_tone = 0
        for x in range(x_areas):
            for y in range(y_areas):
                values[x + 1][y + 1] /= (self.wid_area * self.hei_area)
                cumulative_tone += values[x + 1][y + 1]

        average_tone = cumulative_tone / (x_areas * y_areas)

        return average_tone, values

    def GetTones(self):
        """
        :return: Returns list of all available tones.
        Searches through Characters/Sorted directory.
        """
        tones_raw = listdir("Characters/Sorted")
        tones = []

        for tone in tones_raw:
            tones.append(int(tone))

        return tones

    def CountTones(self):
        tone_counts = []
        for tone in self.char_arrays:
            tone_counts.append(len(tone))

        return tone_counts

    def InvertTones(self):
        """
        Changes "value"s in self.tones to "self.char_area - value"s
        Inverts order in self.tone_counts
        """
        tones_inverted = []
        for tone in self.tones:
            tones_inverted.append(self.char_area - tone)

        self.tones = sorted(tones_inverted)

        tone_counts_inverted = []
        for x in range(len(self.tone_counts)):
            tone_counts_inverted.append(self.tone_counts[self.char_area - x])

        self.tone_counts = tone_counts_inverted

    def InvertCharArrays(self):
        """
        Changes order of self.char_arrays
        """
        char_arrays_inverted = []

        for x in range(len(self.char_arrays)):
            char_arrays_inverted.append(self.char_arrays[self.char_area - x])

        self.char_arrays = char_arrays_inverted

    def GenerateCharArrays(self):
        """
        Loads character images into list for faster access.
        Final list has 36 sublists, each for particular tone (0-35) those contain lists of particular shape that
        describe character.
        LIST[TONE][NUMBER OF CHARACTER OF CHOICE][X AXIS][Y AXIS]

        :return: Returns list as described above.
        """
        CharacterArray = [[] for x in range(5 * 7 + 1)]
        for tone in self.tones:
            characters = listdir("Characters/Sorted/" + str(tone))
            for character in characters:
                Addition = [[0 for y in range(7)] for x in range(5)]
                im = Image.open("Characters/Sorted/" + str(tone) + "//" + character)
                pixels = im.load()

                for x in range(5):
                    for y in range(7):
                        Addition[x][y] = pixels[x,y][0]

                CharacterArray[tone].append(Addition)
        return CharacterArray

    def PrintCharArray(self, CharArray):
        """
        Unused function written for Testing of GenerateCharArrays

        :param CharArray: A slice of a CharArrays - List[X axis][Y axis]

        Prints the characters using "M" and "-"
        """
        for y in range(7):
            for x in range(5):
                if CharArray[x][6-y] == 0:
                    print("M",end="")
                else:
                    print("-",end="")
            print()

    def FindFit(self, ToneToFit):
        """
        For each area finds the best fitting tone, which it returns.

        :param ToneToFit:  Value (even decimal) for which
        :return:
        """
        if ToneToFit <= 0:
            return 0
        elif ToneToFit >= 255:
            return 35

        ToneToFit *= 35 / 255

        fit = 0

        for x in range(self.tonesLength):
            if self.tones[x] > ToneToFit:
                fit = x
                break

        if ToneToFit - self.tones[fit - 1] <= self.tones[fit] - ToneToFit:
            return self.tones[fit - 1]
        return self.tones[fit]

    def GenerateASCII(self):
        """
        Calls other function and ultimately generates ASCII-art:
        1) .FixResolution
        2) .CalculateValues
        2.5) .InvertTones, .InvertCharArrays
            if average tone of the whole picture is below 128, the background and foreground colours are swapped.
        3) .GenerateCharArrays
        4) creates blank picture for the ASCII-art
        5) Uses Floyd-Steinberg dithering algorithm to create ASCII-art
            https://en.wikipedia.org/wiki/Floyd%E2%80%93Steinberg_dithering
            Shortly, tries to approximate tone of each area as accurately as possible and the error is pushed to
            surrounding areas, so that the overall tone is impacted as little as possible
        6) blank.show()
            Displays ASCII-art through dedicated .png application using PIL.Image.show()
        """

        self.FixResolution()
        average_tone, values = self.CalculateValues()

        if average_tone < 128:
            self.back, self.fore = self.fore, self.back
            self.InvertTones()
            self.InvertCharArrays()

        blank = Image.new("RGB", (self.width, self.height), self.back)
        pixels = blank.load()

        width_s = self.width // self.wid_area
        height_s = self.height // self.hei_area

        coefficient = [255 / 35, 7 / 16, 1 / 16, 5 / 16, 3 / 16]
        for xS in range(width_s):
            for yS in range(height_s):
                fit = self.FindFit(values[xS + 1][yS + 1])
                values[xS + 2][yS + 1] += coefficient[1] * (values[xS + 1][yS + 1] - fit * (coefficient[0]))
                values[xS + 2][yS + 2] += coefficient[2] * (values[xS + 1][yS + 1] - fit * (coefficient[0]))
                values[xS + 1][yS + 2] += coefficient[3] * (values[xS + 1][yS + 1] - fit * (coefficient[0]))
                values[xS + 0][yS + 2] += coefficient[4] * (values[xS + 1][yS + 1] - fit * (coefficient[0]))

                char_of_choice = randint(0, self.tone_counts[fit] - 1)
                for x in range(self.wid_area - 2):
                    for y in range(self.hei_area - 2):

                        if self.char_arrays[fit][char_of_choice][x][y] == 0:
                            pixels[xS * self.wid_area + x + 1, yS * self.hei_area + y + 1] = self.fore

        blank.show()

def GetRGB(default_tone, input):
    """
    :param default_tone:     Only used in case of invalid input to return (0,0,0)/(255,255,255)
    :param input:           User input
    :return:                RBG tuple, preferable from user input
    """
    try:
        inputs = input.split(",")
        values = []

        for item in inputs:
            number = int(item)

            if number < 0 or number > 255:
                return (default_tone * 255, default_tone * 255, default_tone * 255)

            values.append(number)

        return (values[0], values[1], values[2])


    except ValueError:
        return (default_tone * 255, default_tone * 255, default_tone * 255)

def Input():
    """
    Function for input handling
    """
    print("Zadejte jméno obrázku:")
    path_input = input()

    while not path.isfile(path_input):
        path_input = input("Zadaný soubor je nepřístupný, nebo neexistuje. Zkuste zadat jiný. Pro ukončení stiskněte \"Enter\"\n")
        if path_input == "":
            break

    else:
        print("Pokud se nepovede přečíst hodnoty, tak použijeme defaultní.")
        back = GetRGB(1, input("Zadejte barvu nahrazující bílou třemi čísly oddělenými pouze čárkami:\n"))

        fore = GetRGB(0, input("Zadejte barvu nahrazující černou třemi čísly oddělenými pouze čárkami:\n"))

        ascii_art = ASCII(path_input, fore, back)
        ascii_art.GenerateASCII()

Input()
