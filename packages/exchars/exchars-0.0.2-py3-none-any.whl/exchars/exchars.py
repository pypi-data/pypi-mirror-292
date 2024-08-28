class Chars(object):
    badChars = []

    def getCharsExceptBad(self):
        '''Return the joined result of the filtered character list'''
        return ''.join(self.getCharsList())

    def getCharsList(self):
        '''Use list comprehension to filter and convert characters'''
        return [
            chr(x) for x in range(1, 256)
            if '{:02x}'.format(x) not in self.badChars
        ]

    def getHexGrid(self, strLength=16):
        '''Use list comprehension to generate the hex grid'''
        bytes = self.getCharsList()
        hex_grid = [
            self.byteToHex(character) + (" " if (i + 1) % strLength else "\n")
            for i, character in enumerate(bytes)
        ]
        return ''.join(hex_grid).strip()

    def byteToHex(self, byteStr):
        '''Convert a byte string to its hex string representation e.g. for output.'''
        return ' '.join(f"{ord(x):02X}" for x in byteStr)

    def getConvertedBadChars(self):
        '''Use list comprehension for converting bad chars'''
        return repr(''.join(chr(int(char, 16)) + "  " for char in self.badChars))

    def cyclic(self, length):
        '''Generate random chars for finding exploits'''
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lower = "abcdef"
        digits = "0123456789"

        pattern = ""

        total_combinations = len(upper) * len(lower) * len(digits)

        for i in range(length):
            u_index = (i // (len(lower) * len(digits))) % len(upper)
            l_index = (i // len(digits)) % len(lower)
            d_index = i % len(digits)

            pattern += upper[u_index] + lower[l_index] + digits[d_index]

        return pattern[:length]

    def find(self, needle):
        '''Find the position of a needle in the cyclic pattern.'''
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lower = "abcdef"
        digits = "0123456789"

        needle_len = len(needle)

        for i in range(len(upper) * len(lower) * len(digits)):
            segment = ''.join(
                upper[(i // (len(lower) * len(digits))) % len(upper)] +
                lower[(i // len(digits)) % len(lower)] +
                digits[i % len(digits)]
                for i in range(i, i + needle_len // 3 + 1)
            )
            if needle in segment:
                return i * 3 + segment.find(needle)

        return -1 