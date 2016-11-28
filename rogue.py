import libtcodpy as libtcod
import random, math

from colours import *
from AI import *

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 15

MAP_HEIGHT = 45
MAP_WIDTH = 80

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 20

colour_dark_wall = libtcod.Color(20,20,100)
colour_dark_ground = libtcod.light_sepia + libtcod.Color(15,0,0)
colour_darkest_ground = libtcod.sepia
colour_ground_dust = libtcod.lightest_sepia

class Tile(object):
    #A map tile
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False
        self.char = ' '
        self.bg_colour = libtcod.black
        self.colour = libtcod.white

        self.updateColours()

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: 
            block_sight = blocked
        self.block_sight = blocked

    def updateColours(self):
        '''update our visible and hidden colours'''
        # self.hiddenColour = self.colour * 0.85
        self.hiddenColour = desaturateColour(self.colour)
        # self.bg_hiddenColour = self.bg_colour * 0.85
        self.bg_hiddenColour = desaturateColour(self.bg_colour)


class Desert(Tile):
    '''desert floor'''
    #Desert tile with random background and random dust dots
    def __init__(self, blocked):
        super(Desert, self).__init__(blocked)

        self.char = random.choice([' '] * 10 + ['.', ','])
        self.bg_colour = randomColour(colour_dark_ground, (0.95,1.05))
        self.colour = randomColour([colour_ground_dust]*20 + [libtcod.light_green], (0.95,1.05))
        self.updateColours()


class Door(Tile):
    '''Door Tile Object'''
    def __init__(self, side):
        super(Door, self).__init__(True)
        if side:
            self.char = libtcod.CHAR_DVLINE
        else:
            self.char = libtcod.CHAR_DHLINE

        self.colour = libtcod.dark_amber
        self.bg_colour = libtcod.darkest_amber
        self.updateColours()


class Wall(Tile):
    def __init__(self):
        super(Wall, self).__init__(True)

        self.char = '#'
        self.bg_colour = randomColour(libtcod.darkest_sepia, (1.0,1.85))
        self.colour = libtcod.dark_sepia
        self.updateColours()


class Floor(Tile):
    def __init__(self):
        super(Floor, self).__init__(False)

        self.char = '='
        self.bg_colour = randomColour(libtcod.Color(105,90,60), (0.98,1.00))
        self.colour = libtcod.dark_sepia
        self.updateColours()

class Rect(object):
    #a rectangle on the map
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h


class Object(object):
    #this is a generic object: the player, a monster, an item, the stairs - any form of interactivity
    def __init__(self, x, y, char, colour, blocks=False):
        '''All objects have an x, y, character and colour'''
        self.x = x
        self.y = y
        self.char = char
        self.colour = colour
        self.blocks = blocks

        self.ai = None

    def move(self, dx, dy):
        '''All objects can move'''
        self.x += dx
        self.y += dy

    def draw(self):
        '''All objects need to be drawn'''
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            #set the colour and then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(con, self.colour)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase self
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE) 


class NPC(Object):
    '''basic NPC object'''
    def __init__(self, x, y, char, colour, name = 'Villager', blocks = True, ai=None, physics=None):
        super(NPC, self).__init__(x, y, char, colour, blocks)

        self.name = name

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.physics = ai 
        if self.physics:
            self.physics.owner = self

#####################################################


def handle_keys():

    key = libtcod.console_check_for_keypress(True) #Turn Based
    
    #Toggle Fullscreen:
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_if_fullscreen())
    #Quit
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit' 

    if game_state == 'playing':
        #movement keys:
        if libtcod.console_is_key_pressed(libtcod.KEY_UP) or libtcod.console_is_key_pressed(libtcod.KEY_KP8):
            player_move(0,-1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) or libtcod.console_is_key_pressed(libtcod.KEY_KP2):
            player_move(0,1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) or libtcod.console_is_key_pressed(libtcod.KEY_KP4):
            player_move(-1,0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) or libtcod.console_is_key_pressed(libtcod.KEY_KP6):
            player_move(1,0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_KP1):
            player_move(-1,1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_KP7):
            player_move(-1,-1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_KP9):
            player_move(1,-1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_KP3):
            player_move(1,1)
        else:
            return 'didnt-take-turn'


def player_move(dx, dy):
    '''move the player to destination x, destination y'''

    global fov_recompute

    x = player.x + dx
    y = player.y + dy

    #Attempt to find an interactive object at target destination
    target = None
    for object in objects:
        if object.x == x and object.y == y:
            target = object
            break

    #Check there's an object target
    if target is not None:
        pass
    #Check we're not walking into a wall
    elif map[x][y].blocked:
        pass
    else:
        player.move(dx, dy)
        fov_recompute = True


def make_map():
    global map

    #Make the flat desert
    map = [[Desert(False) for y in xrange(MAP_HEIGHT)] for x in xrange(MAP_WIDTH)]

    #Make a couple of huts
    for room in [Rect(5,8,15,8), Rect(25,7,12,10), Rect(40,8,25,8)]:
        createRoom(room)

    createRoad()


def createRoad(x=0, y=20, w=MAP_WIDTH, h=5):
    global map

    for road_x in xrange(x, x+w):
        for road_y in xrange(y, y+h):

            if 0 <= road_x < MAP_WIDTH and 0 <= road_y < MAP_HEIGHT:
                map[road_x][road_y].bg_colour *= 0.9
                map[road_x][road_y].colour = map[road_x][road_y].bg_colour * 1.1
                map[road_x][road_y].char = '='
                map[road_x][road_y].updateColours()

                #Random chance of affecting border of self
                if random.random() > 0.25:
                    tile = random.choice([(road_x-1, road_y), (road_x+1, road_y), (road_x, road_y-1), (road_x, road_y+1)])
                    if 0 <= tile[0] < MAP_WIDTH and 0 <= tile[1] < MAP_HEIGHT:
                        map[tile[0]][tile[1]].bg_colour *= 0.9
                        map[tile[0]][tile[1]].colour = map[tile[0]][tile[1]].bg_colour * 1.1
                        map[tile[0]][tile[1]].char = '#'
                        map[tile[0]][tile[1]].updateColours()


def createRoom(room, doors = 2):   
    global map

    #Generate the room
    for x in xrange(room.x1, room.x2+1):
        for y in xrange(room.y1, room.y2+1):
            
            if x == room.x1 or x == room.x2 or y == room.y1 or y == room.y2:
                map[x][y] = Wall()
            else:
                map[x][y] = Floor()

    #Add the doors
    numDoors = 0
    while numDoors < doors:
        #X edge or Y edge?
        if random.random() > 0.5:
            #X Axis
            x = random.randint(room.x1+2, room.x2-2)
            y = random.choice([room.y1, room.y2])
            side = False
        else:
            #Y Axis
            x = random.choice([room.x1, room.x2])
            y = random.randint(room.y1+2, room.y2-2)
            side = True

        #Check there's not already a door in this spot, we dont want duplicates occupying the same space
        if type(map[x][y]) != Door:
        
            map[x][y] = Door(side)
            numDoors += 1


def render_all():

    global fov_recompute

    if fov_recompute:
        #recompute FOV if needed (the player moved or something chan ged)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in xrange(MAP_HEIGHT):    
            for x in xrange(MAP_WIDTH):
                
                visible = libtcod.map_is_in_fov(fov_map, x, y)

                if not visible:
                    if map[x][y].explored:
                        #Explored, Invisible tiles - remove detail char and set to greyscale colour 
                        libtcod.console_put_char_ex(con, x, y, ' ', map[x][y].hiddenColour, map[x][y].bg_hiddenColour)
                    else:
                        #UnExplored, Invisible tiles (spaces with a grey tint)
                        libtcod.console_put_char_ex(con, x, y, ' ', libtcod.black, map[x][y].bg_colour * 0.1)
                else:
                    #Visible Tile, set to explored
                    libtcod.console_put_char_ex(con, x, y, map[x][y].char, map[x][y].colour, map[x][y].bg_colour)
                    map[x][y].explored = True


    #draw all objects in list
    for object in objects:
        object.draw()

    #Push out console to the window
    libtcod.console_blit(con, 0,0,SCREEN_WIDTH,SCREEN_HEIGHT, 0,0,0)

####################################################################################################################

libtcod.console_set_custom_font('arial10x10.png', flags=libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Salvage', False)
libtcod.sys_set_fps(15)

con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

playerx = SCREEN_WIDTH / 2
playery = SCREEN_HEIGHT / 2

player = Object(playerx, playery, '@', libtcod.white)
npc = NPC(playerx-5, playery+2, '@', libtcod.blue, ai=BasicNPC())
objects = [player, npc]

game_state='playing'
player_action = None

make_map()

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in xrange(MAP_HEIGHT):
    for x in xrange(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute=True

### MAIN LOOP ###
while not libtcod.console_is_window_closed():

    #Render Screen
    render_all()

    libtcod.console_flush()

    for object in objects:
        object.clear()

    #handle keys and quit if true:
    player_action = handle_keys()
    if player_action == 'exit':
        break

    if game_state == 'playing' and player_action != 'didnt-take-turn':
        for object in objects:
            if object.ai:
                object.ai.take_turn(fov_map)