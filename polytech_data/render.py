import pygame

#Constants for rendering
FPS = 30
TIMESCALE = 10
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

#Initializes the renderer, returning surface
def init_render():
    global state
    #Init pygame
    pygame.init()
    pygame.font.init()
    state['screen'] = pygame.display.set_mode(WINDOW_SIZE)
    state['clock'] = pygame.time.Clock()
    return state['screen']

def stop_render():
    pygame.quit()

def tick():
    "Returns whether to exit"
    global state
    pygame.display.flip()
    state['clock'].tick(FPS)
    state['clock'].screen.fill(WHITE)
    for event in pygame.event.get():
        #Quit if prompted
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.key.K_ESCAPE:
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

def render_node(surface, pos):
    pos = to_screen_space(pos)
    radius = 2 + abs(pos[0])
    pygame.draw.circle(surface, BLACK, (pos[1], pos[2]), radius)

def render_element(surface, poses):
    if len(poses)>2:
        poses = [to_screen_space(pos) for pos in poses]
        poses = [(pos[1], pos[2]) for pos in poses]
        pygame.draw.lines(surface, BLACK, True, poses)

def render_label(surface, pos, text):
    # Load font and render the text label
    global _FONT
    _FONT = _FONT or pygame.font.SysFont("dejavusans", 8)
    label = FONT.render(text, True, BLACK, WHITE)

    #Get where to place
    pos = to_screen_space(pos)
    label_pos = (pos[1], pos[2])

    #Draw to surface
    surface.blit(label, label_pos)
