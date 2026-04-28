import random

def roll(number:int, size:int):
    results = []

    for i in range(number):
        results.append(random.randint(1, size))
    
    return results