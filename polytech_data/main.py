#!/usr/bin/python
import pyuff
import sys
import pygame
from tabulate import tabulate

#Constants for rendering
FPS = 60
TIMESCALE = 10
SIZE = (500, 500)

#Colors
WHITE = (255,255,255)
BLACK = (  0,  0,  0)

#Constants for extracting data
TYPE_VERTEX = 15
TYPE_DISPLACEMENT = 58

ID2_X_DISPLACEMENT = "Response X  Displacement"
ID2_Y_DISPLACEMENT = "Response Y  Displacement"
ID2_Z_DISPLACEMENT = "Response Z  Displacement"

#Don't print these keys. Junk data
IGNORE_LIST = ["unit_exp", "axis_lab", "func_type", "ver_num", "ref_ent_name", "orddenom"]
GROWTH_SCALAR = 50_000
DISPLACEMENT_POINTS = 10_000

#Just holds xyz data
class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def tuple(self):
        return self.x, self.y, self.z

    def copy(self):
        return Vec3(self.x, self.y, self.z)

    def __add__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            raise Exception("You can't add other shit to a vec3, numbnuts")


#Class which holds the initial position and all displacements
#of a single vertex
class NodeData:
    @classmethod
    def get_base_position(cls, data_set, target_node_id):
        '''
        Returns a Vec3 containing the specified node's base position
        Returns None on failure
        '''
        for d in data_set:
            if d.get('type') == TYPE_VERTEX:
                #Once found vertex dataset, search for the correct node index
                for node_index, node_id in enumerate(d.get('node_nums')):
                    if node_id == target_node_id:
                        vert_x = d.get('x')[node_index]
                        vert_y = d.get('y')[node_index]
                        vert_z = d.get('z')[node_index]

                        #Construct base position
                        vert = Vec3(vert_x, vert_y, vert_z)
                        return vert


        #If failed to find, just give up and go home
        return None

    @classmethod
    def get_displacements(cls, data_set, node_id):
        '''
        Returns (displacements, times), where
        - displacements = is a list of Displacement objects,
        - times = a list of decimal values representing times
        Both lists are of equivalent length, and correspond 1:1 in elements.
        Returns None,None on failure
        '''
        #First gather the data from data_set
        disp_x, disp_y, disp_z, disp_times = None, None, None, None
        for d in data_set:
            if d.get('type') == TYPE_DISPLACEMENT and d.get('rsp_node') == node_id:
                id2 = d.get('id2')
                if      id2 == ID2_X_DISPLACEMENT:
                    disp_x = d.get('data')
                elif    id2 == ID2_Y_DISPLACEMENT:
                    disp_y = d.get('data')
                elif    id2 == ID2_Z_DISPLACEMENT:
                    disp_z = d.get('data')
                    disp_times = d.get('x') # COuldve been anywhere else but whatever

        #If all goes well we will return a valid list, else nothing
        if (disp_x is not None) and (disp_y is not None) and (disp_z is not None) and (disp_times is not None):
            #Combine them
            return [Vec3(x,y,z) for x,y,z in zip(disp_x, disp_y, disp_z)], disp_times
        else:
            #Return nothing if invalid
            return None, None

    #Constructs the vertex data out of the givend ata set
    def __init__(self, data_set, node_id):
        #Find vertex data set
        self.base_postion = NodeData.get_base_position(data_set, node_id)

        #If didn't find vertex data set, fail
        if not self.base_postion:
            raise Exception("Failed to find vertex position for node_id {}".format(node_id))

        #Now find displacements
        self.displacements, self.disp_times = NodeData.get_displacements(data_set, node_id)
        if (self.displacements is None) or (self.disp_times is None):
            raise Exception("Failed to find displacements/times for node_id {}".format(node_id))

#Pretty prints all the keys in a dict, ignoring those keys in IGNORE_LIST
def print_keys(elem):
    kvp = []
    for key in elem:
        val = elem[key]

        if not any(ielem in key for ielem in IGNORE_LIST):
            kvp.append([key, val])

    #If any kvp's valid in element, print them outs
    if kvp:
        print(tabulate(kvp, headers=['key', 'value']))
        input()

def draw_point(surface, x, y, z):
    radius = 2 + abs(x)
    pygame.draw.circle(surface, BLACK, (y, z), radius)

#Converts from the [-1,1] space to SIZE
def to_screen_space(x,y,z):
    #Convert to fraction of [-1,1]
    fy = (y + 1) / 2
    fz = (z + 1) / 2
    
    #Convert to rough screen space
    sy = fy * SIZE[0]
    sz = fz * SIZE[1]

    #Bound to screen
    sy = max(0, min(sy, SIZE[0] - 1))
    sz = max(0, min(sz, SIZE[1] - 1))

    return int(x*GROWTH_SCALAR), int(sy), int(sz)

#Draws a single NodeData object
def draw_node(surface, node_data, disp_index=-1):
    if disp_index == -1:
        displacement = Vec3()
    else:
        displacement = node_data.displacements[disp_index]
    #Build position of node at given time
    pos = (node_data.base_postion + displacement).copy()

    #Convert x and y to screen space
    screen_pos = Vec3(*to_screen_space(*pos.tuple()))

    #Draw
    draw_point(surface, *screen_pos.tuple())

def main(filename):
    #Open the UFF data
    data_file = pyuff.UFF(filename)
    data_set = data_file.read_sets()


    #Print out all our data
    for datum in data_set:
        #print_keys(datum)
        pass

    #Get vertices
    node_data = [NodeData(data_set, node_num) for node_num in range(1,25)]

    #Init pygame
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()

    #Main loop
    done = False
    i=0
    while not done:
        #Handle events
        for event in pygame.event.get():
            #Quit if prompted
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                done = True


        #Render stuff
        screen.fill(WHITE)
    
        #Draw all points to screen.
        i = (i+TIMESCALE) % DISPLACEMENT_POINTS
        print(i)
        for node in node_data:
            draw_node(screen, node,i)

        #Push all rendered data to screen
        pygame.display.flip()

        #Set fps
        clock.tick(FPS)


    pygame.quit()


if __name__ == '__main__':
    #If given, read from a particular file
    if len(sys.argv) < 2:
        main("test.unv")
    else:
        for filename in sys.argv[1:]:
            print("Running for {}".format(filename))
            main(filename)

