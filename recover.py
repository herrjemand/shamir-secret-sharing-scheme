class Lagrange():
    def __init__(self):
        pass

    # https://en.wikipedia.org/wiki/FOIL_method#Table_as_an_alternative_to_FOIL
    def antidiagonal_polynomial_reduce(self, polynomial_table):
        antidiagonals = []

        x_len = len(polynomial_table)
        y_len = len(polynomial_table[0])

        x_dir = 1
        y_dir = -1

        x, y = 0, 0
        antidiagonal = []
        while True:

            if (x + x_dir > x_len and y == y_len - 1) \
            or (y + y_dir > y_len and x == x_len - 1):
                break

            antidiagonal.append(polynomial_table[x][y])

            if (x + x_dir >= x_len or x + x_dir < 0) and (y + y_dir < y_len):
                x_dir, y_dir = y_dir, x_dir
                y   += 1

                antidiagonals.append(antidiagonal)
                antidiagonal = []

                continue

            elif (y + y_dir >= y_len or y + y_dir < 0):
                x_dir, y_dir = y_dir, x_dir
                x   += 1

                antidiagonals.append(antidiagonal)
                antidiagonal = []

                continue

            x = x + x_dir
            y = y + y_dir

        polynomial = list(map(lambda antidiagonal: sum(antidiagonal), antidiagonals))

        return polynomial


    # https://en.wikipedia.org/wiki/FOIL_method#Table_as_an_alternative_to_FOIL
    def table_polynomial_expansion(self, polyA, polyB):

        polynomial_table = []
        for coofA in polyA:
            row = []
            for coofB in polyB:
                row.append(coofA * coofB)

            polynomial_table.append(row)

        return self.antidiagonal_polynomial_reduce(polynomial_table)


    def lagrange_interpolate(self, xi, points):

        monomials = []
        for point in points:
            xj = point['id']
            if xj != xi:
                denominator = xi - xj
                monomials.append([1 / denominator, xj / denominator])

        polynomial = []

        while len(monomials):
            monomial = monomials.pop()

            if polynomial == []:
                polynomial = monomial
                continue

            polynomial = self.table_polynomial_expansion(polynomial, monomial)

        return polynomial

    def recover(self, block):
        p      = block['prime']
        points = block['points']

        for point in points:
            point['li'] = self.lagrange_interpolate(point['id'], points)

        print(points)


class RecoverSecret():
    def __init__(self):
        self.INDEX_SIZE = 1  # 1 byte
        self.BLOCK_SIZE = 64 # 64 byte
        self.PRIME_SIZE = int(self.BLOCK_SIZE / 2)

    def recover(self, SHADOWS):

        # Splitting shadows
        shadow_objects = []
        shift = self.BLOCK_SIZE * 2 # hex char is 4 bites
        for shadow in SHADOWS:
            shadow_objects.append({
                'id'    : int(shadow[: self.INDEX_SIZE * 2 ], 16),
                'blocks': [shadow[self.INDEX_SIZE * 2:][i: i + shift] 
                            for i in range(0, len(shadow) - self.INDEX_SIZE * 2, shift)]
            })


        # Generating recovery blocks
        blocks_raw = []
        blocks_q = sum([len(shadow['blocks']) for shadow in shadow_objects])
        while blocks_q:
            points = []
            for shadow in shadow_objects:
                points.append({ 
                    'id'     : shadow['id'],
                    'shadow' : shadow['blocks'].pop()  
                })

                blocks_q = blocks_q - 1

            blocks_raw.append(points)


        # Formating points
        blocks_fomated = []
        for recovery_block in blocks_raw:
            prime = ''
            points = []
            for point in recovery_block:
                p = point['shadow'][:self.PRIME_SIZE * 2]
                s = point['shadow'][self.PRIME_SIZE * 2:]

                if prime == '':
                    prime = p
                elif prime != p:
                    raise

                point['shadow'] = int(s, 16)

                points.append(point)

            points = sorted(points, key=lambda k: k['id'])
            prime  = int(prime, 16)

            blocks_fomated.append({
                'prime'  : prime,
                'points' : points
            })

        blocks_recovered = []
        for block in blocks_fomated:
            interpolator    = Lagrange()
            block_recovered = interpolator.recover(block)
            blocks_recovered.append(block_recovered)

        return blocks_fomated