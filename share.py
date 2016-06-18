from os import urandom
from Crypto.Util import number

def hexi(WIDTH, INT):
    """
        Converts int to hex with padding
    """
    assert WIDTH > 0
    return ('%0' + str(WIDTH) + 'X') % INT

class Polynomial():
    def __init__(self, THRESHOLD, PARTIES):
        """
            Shamir THRESHOLD size polynomial constructor
        """
        assert THRESHOLD > 0
        assert PARTIES > 0
        assert PARTIES >= THRESHOLD

        self.THRESHOLD       = THRESHOLD
        self.PARTIES         = PARTIES

        self.BLOCK_SIZE      = 30 # 30 bytes
        self.PRIME_SIZE      = 32 # 32 bytes
        self.COOFICIENT_SIZE = self.PRIME_SIZE + 8 # Cooficients always 8 byte larger then PRIME
        self.SHADOW_SIZE     = 32 # 32 bytes

        self.P               = number.getPrime(self.PRIME_SIZE * 8)

        self.POLYNOMIAL_COEFFICIENTS = [int(urandom(self.COOFICIENT_SIZE).hex(), 16) for i in range(THRESHOLD)]

    def generate(self, SECRET_BLOCK):
        """
            Generates SECRET_BLOCK shadows
        """
        assert SECRET_BLOCK <= 2 ** (self.BLOCK_SIZE * 8) # Less then 32 bytes

        blocks = []

        # Calculating polynomials
        POLYLEN = len(self.POLYNOMIAL_COEFFICIENTS)
        for PARTY in range(1, self.PARTIES + 1):
            polynomial     = [self.POLYNOMIAL_COEFFICIENTS[i] * (PARTY ** (POLYLEN - i)) for i in range(POLYLEN)]
            polynomial_sum = sum(polynomial) + SECRET_BLOCK

            shadow_int = polynomial_sum % self.P

            blocks.append(shadow_int)

        return {
            'blocks': blocks,
            'prime' : self.P
        }

class ShareSecret():
    def __init__(self, THRESHOLD, PARTIES):
        """
            Shamir Secret Share Scheme
        """
        assert THRESHOLD > 0
        assert PARTIES > 0
        assert PARTIES >= THRESHOLD

        self.THRESHOLD   = THRESHOLD
        self.PARTIES     = PARTIES
        self.BLOCK_SIZE  = 30 # 30 bytes
        self.SHADOW_SIZE = 32 # 32 bytes


    def generate(self, SECRET):
        """
            generate function takes SECRET string and returns
            an array of hexadecimal encoded SECRET shadows
        """

        assert type(SECRET) == str

        hex_secret      = SECRET.encode('utf-8').hex()
        shift           = self.BLOCK_SIZE * 2 # Hex 4bit per char
        blocks_secret   = [hex_secret[i: i + shift] for i in range(0, len(hex_secret), shift)]

        # Generate block shadows
        blocks_int      = []
        for i in range(len(blocks_secret)):
            poly  = Polynomial(self.THRESHOLD, self.PARTIES)
            block = poly.generate(int(blocks_secret[i], 16))

            blocks_int.append(block)

        # Convert shadows to hex
        blocks_hex = []
        for block in blocks_int:
            block_hex = [hexi(self.SHADOW_SIZE * 2, + block['prime']) + hexi(self.SHADOW_SIZE * 2, block_shadow) 
                for block_shadow in block['blocks'] ]

            blocks_hex.append(block_hex)

        # Map merge blocks
        shadows = []
        while len(blocks_hex) > 0:
            if not len(shadows):
                shadows = blocks_hex.pop()
                continue

            shadows = list(map(lambda a, b: a + b, shadows, blocks_hex.pop()))

        # Index blocks
        for i in range(len(shadows)):
            shadows[i] = hexi(2, i + 1) + shadows[i]

        return shadows