import libtcodpy as libtcod
import random

def randomColour(baseColour=libtcod.black, randomRange=(0.5,1.5)):
    '''
        returns a random colour - will select random.choice from list if applicable
        @param baseColour | base libtcod.color or [libtcod.colour, libtcod.colour ... ]
        @param randomRange | tuple min max multiplication of base colour
        @return libtcod.colour
    '''

    if type(baseColour) is list:
        baseColour = random.choice(baseColour)

    return baseColour * random.uniform(randomRange[0], randomRange[1])


def desaturateColour(colour):
    '''take input colour and make it greyscale to lowest value'''
    lowest = 226
    for c in colour:
        if c < lowest:
            lowest = c

    return libtcod.Color(lowest, lowest, lowest)