import math, random
import time, traceback
from game import Game

# CAT, CHEESE AND TRAP AGENT
class Agent:

    def __init__(self, game):
        self.game = game
        self.score = 0
        self.learners = []
        self.prev_state = None
        self.prev_action = None

    def add_learner(self, learner):
        self.learners.append(learner)

    def item_at(self, coord):
        if self.game.cheese == coord:
            return 'cheese'
        elif self.game.trap == coord:
            return 'trap'
        return ''

    def offset(self, x, y, mouse=None):
        if not mouse:
            mouse = self.game.mouse
        x += mouse[0]
        y += mouse[1]
        # loop the arena
        x = (x + self.game._cw) % self.game._cw
        y = (y + self.game._ch) % self.game._ch
        return x, y

    def get_woff(self, x, y, mouse=None):
        item = self.item_at(self.offset(x,y, mouse=mouse))
#       print '{0} at {1}, {2}'.format(item, *self.offset(x, y))
        if item == 'cheese':
            return 1
        if item == 'trap':
            return -1
        return 0

    def transform(self, x, y):
        d = self.game.direction
        if d == 'right':
            x1 = x
            y1 = y
            x  = y1
            y  = x1
        elif d == 'up':
            x = -x
            y = -y
        elif d == 'left':
            x1 =  x
            y1 =  y
            x  = -y1
            y  = -x1
        # 'down' = no transformation

        return x,y

    # FOV is a the state for the agent
    # the cone counts from left to right and goes size far out
    # it widens as it sees further
    def get_fov(self, size, m=None, d=None):
        def make_odd(x):
            if x % 2 == 0:
                return x - 1
            return x
        mouse = self.game.mouse
        direction = self.game.direction
        if m:
            mouse = m
        if d:
            direction = d
        # assume d is up
        cone = []
        for level in xrange(0, size + 1):
            width = max(3, make_odd(2+level))
            row = []
            for block in xrange(width):
                # transform x and y based on direction
                x,y = self.transform(block - width/2, level)
                row.append(self.get_woff(x, y, mouse)) # get whatever is at x,y
            if direction == 'up': # edge case, mirror around y axis
                row = row[::-1]
            cone.append(row)
        fov = self.create_cone(cone)
        if self.game.easy:
            return fov[0]
        return fov

    def create_cone(self, cone):
        flat = [i for s in cone for i in s]
#       print cone
#       print flat
        bstr = ''.join(map(str,flat))
        cheese = int(bstr.replace('-1','0')[::-1], 2)
        traps = int(bstr.replace('-1', '2').replace('1', '0').replace('2', '1')[::-1], 2)
#       print '{0} produced {1}'.format(bstr, cheese)
        return cheese, traps

    def check_reward(self): 
        if self.game.score > self.score:
            self.score = self.game.score
            return 1
        elif self.game.score < self.score:
            self.score = self.game.score
            return -1
        return 0

    def action(self, act):
        self.game.play(act)
    
    def reset_game(self):
        self.score = 0
        self.game.reset()

