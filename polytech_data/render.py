import pygame
import numpy as np

#Constants for rendering
FPS = 30
WINDOW_SIZE = (500, 500)

#Colors
WHITE = (255,255,255)
BLACK = (  0,  0,  0)
BLUE  = (  0,  0,255)

#Rendering constants
GROWTH_SCALAR = 50_000

#Singletonian
_FONT = None #Set later

state = {}

def init_render():
    global state
    #Init pygame
    pygame.init()
    pygame.font.init()
    state['screen'] = pygame.display.set_mode(WINDOW_SIZE)
    state['clock'] = pygame.time.Clock()

def stop_render():
    pygame.quit()

def tick():
    "Returns whether to exit"
    global state

    #Cycle image
    pygame.display.flip()
    state['clock'].tick(FPS)
    state['screen'].fill(WHITE)

    #Handle events
    for event in pygame.event.get():
        #Quit if prompted
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if pygame.key.name(event.key) == "escape":
                return True

    return False

#Converts from the [-1,1] space toWINDOW_SIZE
def to_screen_space(pos):
    #Convert to fraction of [-1,1]
    pos = pos.copy()
    pos[1] = (pos[1] + 1) / 2
    pos[2] = (pos[2] + 1) / 2
    
    #Convert to rough screen space
    pos[1] *= WINDOW_SIZE[0]
    pos[2] *= WINDOW_SIZE[1]

    #Bound to screen
    pos[1] = max(0, min(pos[1], WINDOW_SIZE[0] - 1))
    pos[2] = max(0, min(pos[2], WINDOW_SIZE[1] - 1))

    #Scale growth
    pos[0] *= GROWTH_SCALAR
    return pos.astype(np.int32)

def _draw_node(pos):
    '''
    Draws a node representation at pos
    '''
    global state
    surface = state['screen']
    pos = to_screen_space(pos)
    radius = 2 + abs(pos[0])
    pygame.draw.circle(surface, BLACK, (pos[1], pos[2]), radius)

def render_node(node_datum):
    '''
    Renders the given node
    '''
    pos = node_datum.position
    _draw_node(pos)

def render_displaced_node(node_datum, disp_datum, index):
    '''
    Renders a given node with displacement
    '''
    pos = node_datum.position
    disp = disp_datum.disp_vecs[index]
    _draw_node(pos + disp)

def _draw_element(poses, color=BLACK):
    '''
    Draws a element representation at the given position 
    sequence
    '''
    global state
    surface = state['screen']
    poses = [to_screen_space(pos) for pos in poses]
    poses = [(pos[1], pos[2]) for pos in poses]
    pygame.draw.lines(surface, color, True, poses)


def render_element(elem_datum, all_node_data):
    '''
    Renders a given element using the supplied node data
    '''
    #Get nodes of the element
    nodes = [all_node_data[l] for l in elem_datum.nodes]
    #Extract their position
    poses = [n.position for n in nodes]
    #Draw
    _draw_element(poses, elem_datum.color)

def render_displaced_element(elem_datum, all_node_data, all_disp_data, disp_index):
    #Get appropriate nodes and disps
    nodes = [all_node_data[l] for l in elem_datum.nodes]
    disps = [all_disp_data[l] for l in elem_datum.nodes]

    #Reduce to vector forms
    bases = [n.position for n in nodes]
    offs = [d.disp_vecs[disp_index] for d in disps]

    #Sum them
    poses = [b+o for b,o in zip(bases, offs)]
    _draw_element(poses, elem_datum.color)

def _draw_label(pos, text):
    # Load font and render the text label
    global state
    global _FONT
    _FONT = _FONT or pygame.font.SysFont("dejavusans", 8)
    label = FONT.render(text, True, BLACK, WHITE)
    surface = state['screen']

    #Get where to place
    pos = to_screen_space(pos)
    label_pos = (pos[1], pos[2])

    #Draw to surface
    surface.blit(label, label_pos)
