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


        blocks_fomated = []
        # Formating points
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
            prime = int(prime, 16)

            blocks_fomated.append({
                'prime'  : prime,
                'points' : points
            })


        return blocks_fomated