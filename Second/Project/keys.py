import random

class Keys:

    def __init__(self, key_size=1024):
        self.key_size = key_size
        self.p, self.q = self.create_pq(key_size)
        self.euler_function = (self.p - 1)*(self.q - 1)
        self.n = self.p * self.q

    def is_prime(self,number):
        # https://www.geeksforgeeks.org/how-to-generate-large-prime-numbers-for-rsa-algorithm/
        # Miller-Rabin test for prime
        if number == 0 or number == 1 or number == 4 or number == 6 or number == 8 or number == 9:
            return False

        if number == 2 or number == 3 or number == 5 or number == 7:
            return True
        s = 0
        d = number - 1
        while d % 2 == 0:
            d >>= 1
            s += 1
        assert (2 ** s * d == number - 1)

        def trial_composite(a):
            if pow(a, d, number) == 1:
                return False
            for i in range(s):
                if pow(a, 2 ** i * d, number) == number - 1:
                    return False
            return True
            # ilosc iteracji
        for i in range(10):
            # używa os.urandom() ktore wedlug dokumentacji opiera sie na wsparciu sprzetowym gwarantujac zabezpieczenie kryptograficzne
            a = random.SystemRandom().randint(2, number)
            if trial_composite(a):
                return False

        return True

    def prime_generator(self,prime_binary_size):
        while True:
            number = random.SystemRandom().randint(2 ** (prime_binary_size - 1), 2 ** prime_binary_size - 1)
            if self.is_prime(number): return number

    def create_pq(self, n_size):

        p_size = int(n_size / 2) + random.SystemRandom().randint(int(n_size / 100),
                                                    int(n_size / 10))
        q_size = n_size - p_size
        p, q = 0, 0
        while (p * q).bit_length() != n_size or p == q:
            p = self.prime_generator(p_size)
            q = self.prime_generator(q_size)
        return p, q

    def create_e(self, p, q):
        phi = (p - 1) * (q - 1)
        if phi > 65537: # 2^16+1 prime number, dla optymalizacji
            return 65537
        else:
            e = phi - 1
            while True:
                if self.is_prime(e): return e
                e = e - 2

    def greatest_common_divisor(self, a, b):
        """ algorytm Euklidesa """
        if b == 0:
            return a
        else:
            return self.greatest_common_divisor(b, a % b)

    @staticmethod
    def create_d(e, p, q):
        """ d = e^-1 %phi """
        phi = (p - 1) * (q - 1)
        # https://stackoverflow.com/questions/18940194/using-extended-euclidean-algorithm-to-create-rsa-private-key
        u1, u2, u3 = 1, 0, e
        v1, v2, v3 = 0, 1, phi
        while v3 != 0:
            q = u3 // v3
            v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
        return u1 % phi

    def create_publc_key(self):
        self.p, self.q = self.create_pq(self.key_size)
        self.e = self.create_e(self.p, self.q)
        return {"e": self.e, "n": self.p*self.q}

    def create_private_key(self):
        self.d = self.create_d(self.e, self.p, self.q)
        return {"d": self.d, "n": self.p * self.q}