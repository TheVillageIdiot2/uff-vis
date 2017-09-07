#!/usr/bin/python
import pyuff
import sys
import pygame
from tabulate import tabulate

#Constants for rendering
FPS = 30
SIZE = (700, 500)

#Colors
WHITE = (255,255,255)
BLACK = (  0,  0,  0)

#Constants for extracting data
TYPE_VERTEX = 15
TYPE_DISPLACEMENT = 58

ID2_X_DISPLACEMENT = "Response X  Displacement"
ID2_Y_DISPLACEMENT = "Response Y  Displacement"
ID2_Z_DISPLACEMENT = "Response Z  Displacement"
DATA_X_KEY = 'y' #For whatever reson the X axis is blank for positions. x corresponds then to y, and y to z
DATA_Y_KEY = 'z'

#Don't print these keys. Junk data
IGNORE_LIST = ["unit_exp", "axis_lab", "func_type", "ver_num", "ref_ent_name", "orddenom"]

#Just holds xyz data
class Vec3:
    def __init__(self):
        self.__init__(0,0,0)

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

#Class which holds the initial position and all displacements
#of a single vertex
class VertexData:
    @classmethod
    def get_base_position(data_set, node_id):
        for d in data_set:
            if d.get('type') == TYPE_VERTEX:
                #Once found, get index of given node id
                vert_index = d.node_nums.index(node_id)
                vert_x = d.x[vert_index]
                vert_y = d.y[vert_index]
                vert_z = d.z[vert_index]

                #Construct base position
                return Vec3(vert_x, vert_y, vert_z)
        return None

    @classmethod
    def get_displacements(data_set, node_id):
        #First gather the data from data_set
        disp_x, disp_y, disp_z = None, None, None
        for d in data_set:
            if d.get('type') == TYPE_DISPLACEMENT and d.get('ref_node') == node_id:
                id2 = d.get('id2')
                if id2 == ID2_X_DISPLACEMENT:
                    disp_x = d.get('data')
                elif id2 == ID2_Y_DISPLACEMENT:
                    disp_y = d.get('data')
                elif id2 == ID2_Z_DISPLACEMENT:
                    disp_z = d.get('data')

        #If all goes well we will return a valid list, else nothing
        if not (disp_x and disp_y and disp_z):
            return None
        else:
            #Comebine them
            return [Vec3(x,y,z) for x,y,z in zip(disp_x, disp_y, disp_z)]



    #Constructs the vertex data out of the givend ata set
    def __init__(self, data_set, node_id):
        #Find vertex data set
        self.base_postion = VertexData.get_base_position(data_set, node_id)

        #If didn't find vertex data set, fail
        if not self.base_postion:
            raise Exception("Failed to find vertex position for node_id {}".format(node_id))

        #Now find displacements
        self.displacements = VertexData.get_displacements(data_set, node_id)
        if not (disp_x and disp_y and disp_z):
            raise Exception("Failed to find displacements for node_id {}".format(node_id))

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

def draw_point(surface, x,y):
    radius = 2
    pygame.draw.circle(surface, BLACK, (x, y), radius)

#Converts from the [-1,1] space to SIZE
def to_screen_space(x,y):
    #Convert to fraction of [-1,1]
    fx = (x + 1) / 2
    fy = (y + 1) / 2
    
    #Convert to rough screen space
    sx = fx * SIZE[0]
    sy = fy * SIZE[1]

    return (int(sx), int(sy))

def get_displacement(data_set, node_id, id_key):
    displacement_sets = [e for e in data_set if e.get('type') == TYPE_DISPLACEMENT]
    node_sets = [e for e in displacement_sets if e.get('rsp_node') == node_id]
    needed_sets = [e for e in node_sets if e.get('id2') == id_key]
    if len(needed_sets):
        return needed_sets[0]
    else:
        raise Exception("Couldn't find {} for node {}".format(id_key, node_id))

def draw_vertex(vertex_dataset, disp_set_x, disp_set_y, disp_set_z):
    pass


def main(filename):
    #Open the UFF data
    data_file = pyuff.UFF(filename)
    data_set = data_file.read_sets()


    #Print out all our data
    for datum in data_set:
        print_keys(datum)

    #Get vertices
    point_data_sets = [d for d in data_set if d.get('type') == TYPE_VERTEX]
    vertex_dataset = point_data_sets[0]

    #Get displacements
    displacements = [d for d in data_set if d.g

    #Init pygame
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()

    #Main loop
    done = False
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
        points_x = point_data[DATA_X_KEY]
        points_y = point_data[DATA_Y_KEY]
        for point in zip(points_x, points_y):
            point = to_screen_space(*point)
            draw_point(screen, *point)

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

