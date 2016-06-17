from os import urandom
from Crypto.Util import number

def hexi(WIDTH, INT):
    """
        Converts int to hex with padding
    """
    assert WIDTH > 0
    return '%' + WIDTH + 'X' % INT

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

        self.BLOCK_SIZE      = 24 # 24 bytes
        self.COOFICIENT_SIZE = 16 # 16 bytes
        self.PRIME_SIZE      = 32 # 32 bytes
        self.SHADOW_SIZE     = 32 # 32 bytes

        self.P               = number.getPrime(self.PRIME_SIZE * 8)

        self.POLYNOMIAL_COEFFICIENTS = [int(urandom(16).hex(), 16) for i in range(THRESHOLD)]

    def generate(self, SECRET_BLOCK):
        """
            Generates SECRET_BLOCK shadows
        """
        assert SECRET_BLOCK <= 2 ** (self.BLOCK_SIZE * 8)

        blocks = []

        POLYLEN = len(self.POLYNOMIAL_COEFFICIENTS)
        for PARTY in range(1, self.PARTIES + 1):
            polynomial     = [self.POLYNOMIAL_COEFFICIENTS[i] * PARTY ** (POLYLEN - i) for i in range(POLYLEN)]
            polynomial_sum = sum(polynomial) + SECRET_BLOCK

            shadow_int = polynomial_sum % self.P

            blocks.append(shadow_int)

        return {
            'blocks': blocks,
            'prime' : self.P
        }

class ShareSecret():
    def __init__(self, THRESHOLD, PARTIES):

        assert THRESHOLD > 0
        assert PARTIES > 0
        assert PARTIES >= THRESHOLD

        self.THRESHOLD  = THRESHOLD
        self.PARTIES    = PARTIES
        self.BLOCK_SIZE = 24 # 24 bytes


    def generate(self, SECRET):

        assert type(SECRET) == str

        secret_hex      = SECRET.encode('utf-8').hex()
        shift           = self.BLOCK_SIZE * 2 # Hex 4bit per char
        blocks_secret   = [secret_hex[i: i + shift] for i in range(0, len(secret_hex), shift)]

        blocks_int      = []
        for i in range(len(blocks_secret)):
            poly  = Polynomial(self.THRESHOLD, self.PARTIES)
            block = poly.generate(int(blocks_secret[i], 16))

            blocks_int.append(block)

        return blocks_int

