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
X_KEY = 'z'
Y_KEY = 'y'

#If given, read from a particular file
if len(sys.argv) < 2:
    filename = "test.unv"
else:
    filename = sys.argv[1]

#Open the UFF data
data_file = pyuff.UFF(filename)
data_set = data_file.read_sets()

#Don't print these keys. Junk data
ignore_list = []#["unit_exp", "axis_lab"]

def print_keys(elem):
    kvp = []
    for key in elem:
        val = elem[key]
        if elem.get('type')  != 15:
            continue

        if not any(ielem in key for ielem in ignore_list):
            kvp.append([key, val])

    #If any kvp's valid in element, print them outs
    if len(kvp):
        print(tabulate(kvp, headers=['key', 'value']))
        input()


#Print out all our data
for datum in data_set:
    break
    print_keys(datum)

#Get canvas points
point_data_sets = [d for d in data_set if d.get('type') == 15]
point_data = point_data_sets[0]

#Init pygame
pygame.init()
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()

#Converts from the [-1,1] space to SIZE
def to_screen_space(x,y):
    #Convert to fraction of [-1,1]
    fx = (x + 1) / 2
    fy = (y + 1) / 2
    
    #Convert to rough screen space
    sx = fx * SIZE[0]
    sy = fy * SIZE[1]

    return (int(sx), int(sy))


def draw_point(x,y):
    radius = 2
    pygame.draw.circle(screen, BLACK, (x, y), radius)

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

    points_x = point_data[X_KEY]
    points_y = point_data[Y_KEY]
    for point in zip(points_x, points_y):
        print(point)
        point = to_screen_space(*point)
        print(point)
        draw_point(*point)

    #Push all rendered data to screen
    pygame.display.flip()

    #Set fps
    clock.tick(FPS)


pygame.quit()

