import libtcodpy as libtcod
import random, math
'''
    AI Components
'''

class BasicNPC(object):
    def __init__(self, movement=None):
        self.movement = movement

    def take_turn(self, fov_map):
        print 'The ', self.owner.name + ' stares aimlessly.'

        if libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):

            #Move in random direciton
            randomX = random.choice([0]*20 + [-1,1])
            randomY = random.choice([0]*20 + [-1,1])

            # self.move_towards(randomX, randomY)
            self.owner.move(randomX, randomY)

    def move_towards(self, target_x, target_y):
        #Get vector between two points
        dx = target_x - self.owner.x
        dy = target_y - self.owner.y
        distance = math.sqrt(dx**2 + dy**2)

        #normalise length
        dx = int(round(dx/distance))
        dy = int(round(dy/distance))

        #Move
        self.owner.move(dx, dy)
