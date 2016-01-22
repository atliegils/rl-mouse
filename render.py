import pygame

# setup code, constants
WIN_WIDTH = 640
WIN_HEIGHT = 480
CELL_SIZE = 20
assert WIN_WIDTH  % CELL_SIZE == 0, "Window width must be a multiple of cell size."
assert WIN_HEIGHT % CELL_SIZE == 0, "Window height must be a multiple of cell size."
CELL_WIDTH  = int(WIN_WIDTH  / CELL_SIZE)
CELL_HEIGHT = int(WIN_HEIGHT / CELL_SIZE)
# COLOR       R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
YELLOW    = (255, 255,   0)
DARKGREEN = (  0, 155,   0)
BLUE      = (  0,   0, 255)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK


class Renderer:
    display = None
    basic_font = None
    _cc = CELL_SIZE
    _ww = 320
    _wh = 240
    
    def __init__(self, ww, wh):
        self._ww = ww * self._cc
        self._wh = wh * self._cc
        self.display = pygame.display.set_mode((self._ww, self._wh))
        self.basic_font = pygame.font.Font('freesansbold.ttf', 18)
        pygame.display.set_caption('Mouse Game')

    def render(self, items, score):
        self.display.fill(BGCOLOR)
        self.draw_grid()
        self.draw_item(items[0], YELLOW)
        self.draw_item(items[1], RED)
        self.draw_item(items[2], WHITE)
        self.draw_score(score) # draw the score
        pygame.display.update()

    def render_custom(self, item_pairs, score):
        self.display.fill(BGCOLOR)
        self.draw_grid()
        for loc, color in item_pairs:
            self.draw_item(loc, color)
        self.draw_score(score) # draw the score
        pygame.display.update()

    def draw_item(self, item, color):
        c = self._cc
        x = item[0] * c
        y = (self._wh/c - item[1] - 1) * c # render so that higher y coordinates are drawn higher
        therect = pygame.Rect(x, y, c, c)
        pygame.draw.rect(self.display, color, therect)

    def draw_score(self, score):
        surf = self.basic_font.render('Score: %s' % (score), True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (self._ww - 120, 10)
        self.display.blit(surf, rect)

    def draw_grid(self):
        cell_size = self._cc
        for x in range(0, self._ww, cell_size): # draw vertical lines
            pygame.draw.line(self.display, DARKGRAY, (x, 0), (x, self._wh))
        for y in range(0, self._wh, cell_size): # draw vertical lines
            pygame.draw.line(self.display, DARKGRAY, (0, y), (self._ww, y))

