import random


def nRandomNumber(n):
    # uses os.urandom() which is fit for cryptography random number generation
    return random.SystemRandom().randint(2 ** (n - 1) + 1, 2 ** n - 1)


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

def calculate_e(p, q):
     phi = (p-1)*(q-1)
     if phi >65537: return 65537 #2^16+1 prime number
     else:
        e = phi -1
        while True:
            if isMillerRabinPassed(e): return e
            e = e - 2


if __name__ == '__main__':
    while True:
        n = 128
        p = nRandomNumber(n)
        q = nRandomNumber(n)
        if not isMillerRabinPassed(p) or not isMillerRabinPassed(q):
            continue
        else:
            print(n, "bit prime is: \n", p)
            print(n, "bit prime is: \n", q)
            m = p * q
            euler_totient = (p-1)*(q-1)
            print(euler_totient)
            e=calculate_e(p,q)
            d=e^-1 % euler_totient
            public_key = (m,e)
            private_key = (m,d)
            print(f"public key={m},{e}")
            print(f"private key={m},{d}")

            break
