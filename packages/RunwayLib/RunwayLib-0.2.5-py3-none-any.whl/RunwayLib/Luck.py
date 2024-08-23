import random


def testluck(Number1, Number2):
    number = random.randint(Number1, Number2)
    randomnumhald =  number / 2
    if number > randomnumhald:
        return(f"Your Are Lucky luck:{number} from {Number2}")
