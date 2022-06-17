import random



class RSA:
    def __init__(self,bits):
        self.p=self.generatePrimeNumber(bits)
        self.q=self.generatePrimeNumber(bits)
        self.n=self.p * self.q
        self.euler_totient= (self.p-1)*(self.q-1)
        self.e = self.calculate_e(self.p,self.q)
        self.d= self.e^-1 % self.euler_totient
        self.public_key= (self.n,self.e)
        self.private_key = (self.n,self.d)

    def generatePrimeNumber(self,bits):
        while True:
            number = self.nRandomNumber(bits)
            if not self.isMillerRabinPassed(number):
                continue
            else:
                return number

    def nRandomNumber(self,n):
        # uses os.urandom() which is fit for cryptography random number generation
        return random.SystemRandom().randint(2 ** (n - 1) + 1, 2 ** n - 1)


    def isMillerRabinPassed(self,mrc):
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


    def calculate_e(self,p, q):
         phi = (p-1)*(q-1)
         if phi >65537: return 65537 #2^16+1 prime number
         else:
            e = phi -1
            while True:
                if self.isMillerRabinPassed(e): return e
                e = e - 2


if __name__ == '__main__':
    randomRsa = RSA(128)
    print(f"public key = {randomRsa.public_key}")
    print(f"priavte key = {randomRsa.private_key}")
