import random


class RSA:
    def __init__(self, bits):
        self.p = self.generatePrimeNumber(bits)
        self.q = self.generatePrimeNumber(bits)
        self.n = self.p * self.q
        self.euler_totient = (self.p - 1) * (self.q - 1)
        self.e = self.calculate_e(self.p, self.q)
        self.d = pow(self.e, -1, self.euler_totient)
        self.public_key = (self.n, self.e)
        self.private_key = (self.n, self.d)
        self.key_size = bits

    def generatePrimeNumber(self, bits):
        while True:
            number = self.nRandomNumber(bits)
            if not self.isMillerRabinPassed(number):
                continue
            else:
                return number

    def nRandomNumber(self, n):
        # uses os.urandom() which is fit for cryptography random number generation
        return random.SystemRandom().randint(2 ** (n - 1) + 1, 2 ** n - 1)

    @staticmethod
    def isMillerRabinPassed(mrc):
        # Run 20 iterations of Rabin Miller Primality test
        maxDivisionsByTwo = 0
        ec = mrc - 1
        while ec % 2 == 0:
            ec >>= 1
            maxDivisionsByTwo += 1
        assert (2 ** maxDivisionsByTwo * ec == mrc - 1)

        def trialComposite(round_tester):
            if pow(round_tester, ec, mrc) == 1:
                return False
            for i in range(maxDivisionsByTwo):
                if pow(round_tester, 2 ** i * ec, mrc) == mrc - 1:
                    return False
            return True

        # Set number of trials here
        numberOfRabinTrials = 20
        for i in range(numberOfRabinTrials):
            round_tester = random.randrange(2, mrc)
            if trialComposite(round_tester):
                return False
        return True

    def calculate_e(self, p, q):
        phi = (p - 1) * (q - 1)
        if phi > 65537:
            return 65537  # 2^16+1 prime number
        else:
            e = phi - 1
            while True:
                if self.isMillerRabinPassed(e): return e
                e = e - 2

    # def encrypt_ecb(self, raw_idat_data):
    #     encrypted_data = []
    #     step = 8
    #     for i in range(0, len(raw_idat_data), step):
    #         # if len(raw_idat_data) - step * i < step:
    #         raw_idat_data_block = bytes(raw_idat_data[i:i + step])
    #         int_idat_data_block = int.from_bytes(raw_idat_data_block, byteorder="big")
    #         encrypted_int_idat_data_block = pow(int_idat_data_block, self.public_key[1], self.public_key[0])
    #         encrypted_data_bytes = encrypted_int_idat_data_block.to_bytes(step, 'big')
    #         encrypted_data.append(encrypted_data_bytes)
    #     return encrypted_data

    # def decrypt_ecb(self):

    def test_encrypt(self):
        return pow(2137, self.public_key[1], self.public_key[0])

    def test_decrypted(self, mess):
        return pow(mess, self.private_key[1], self.public_key[0])


if __name__ == '__main__':
    randomRsa = RSA(256)
    print(f"public key = {randomRsa.public_key}")
    print(f"priavte key = {randomRsa.private_key}")
    enctpted = randomRsa.test_encrypt()
    print(f"encrypted ={enctpted}")
    hehe = randomRsa.test_decrypted(enctpted)
    print(f"oby papiez= {hehe}")
