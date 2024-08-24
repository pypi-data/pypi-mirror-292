# RunwayLib/luck.py
import random

def luck(Number1, Number2):
    number = random.randint(Number1, Number2)
    randomnumhalf = number / 2
    if number > randomnumhalf:
        return f"You are lucky! Luck: {number} from {Number2}"
    else:
        return f"Not so lucky... Luck: {number} from {Number2}"
