import random
import math

class MouseEnvironment:
    suppressed = False
    high_score = 0

    # default cell size
    def __init__(self, do_render=False):
        self.width = 32
        self.height = 24
        self.do_render = do_render
        if self.do_render:  #   BIG RED NOTICE HERE
            global pygame   # -----------------------
            global render   # Only import into global
            import pygame   #    namespace if the
            import render   #   render flag is set!
            pygame.init()
        self.score = 0
        self.trap   = (0, 0)
        self.mouse  = (0, 0)
        self.cheese = (0, 0)
        self.force_kill = False
        self.cat = False
        self.move_chance = 0.07
        self.easy = False
        self.reset()
        if self.do_render:
            self.r = render.Renderer(self.width, self.height)

    def __del__(self):
        return # don't kill it :p otherwise we can't copy games
        if self.do_render:
            pygame.quit()

    def reset(self):
        self.direction = 'right'
        if not self.easy:
            self.trap   = self.random_location()
        self.mouse  = self.random_location()
        self.cheese = self.random_location()
        self.score = 0

    # custom cell size
    def set_size(self, cw, ch):
        self.width = cw
        self.height = ch
        self.reset()
        if self.do_render:
            del self.r
            self.r = render.Renderer(self.width, self.height)

    def get_size(self):
        return self.width, self.height

    def render(self):
        if self.do_render:
            self.r.render((self.cheese, self.trap, self.mouse), self.score)

    def play(self, action):
        # move the trap if it's a cat
        if self.cat:
            self.move_trap()
        # move the mouse according to action
        self.move(action)
        self.update_score()
        if not self.suppressed:
            self.render()
        if self.force_kill:
            import sys
            sys.exit(-9)

    def pretend(self, action):
        m = self.mouse
        c = self.cheese
        t = self.trap
        d = self.direction

        self.move(action)
        position, direction = self.mouse, self.direction

        self.direction = d
        self.mouse  = m
        self.cheese = c
        self.trap   = t
        return position, direction

    def move(self, action):
        if action == '?':
            action = random.choice(['left', 'right', 'forward'])
        dirs = ['left', 'up', 'right', 'down']
        ind = dirs.index(self.direction)
        # orient the mouse
        if action == 'left':  # counter-clockiwse
            ind = (ind + 3) % 4 
            self.direction = dirs[ind]
        elif action == 'right':       # clockwise
            ind = (ind + 1) % 4 
            self.direction = dirs[ind]
        else: # forward
            pass
        # move it forward
        if self.direction   == 'up':
            self.mouse = (self.mouse[0], self.mouse[1] + 1)
        elif self.direction == 'down':
            self.mouse = (self.mouse[0], self.mouse[1] - 1)
        elif self.direction == 'left':
            self.mouse = (self.mouse[0] - 1, self.mouse[1])
        elif self.direction == 'right':
            self.mouse = (self.mouse[0] + 1, self.mouse[1])

        # loop the arena
        self.mouse = ((self.mouse[0] + self.width) % self.width
                , (self.mouse[1] + self.height) % self.height)

    def move_trap(self):
        dx = max(-1, min(1, self.trap[0] - self.mouse[0]))
        dy = max(-1, min(1, self.trap[1] - self.mouse[0]))
        new_x = self.trap[0]
        new_y = self.trap[1]
        move_x = random.random() < self.move_chance
        move_y = random.random() < self.move_chance
        if move_x:
            new_x = self.trap[0] - dx
        if move_y:
            new_y = self.trap[1] - dy
        if (new_x, new_y) == self.mouse:
            if move_x:
                new_x += dx
            elif move_y:
                new_y += dy
        elif (new_x, new_y) != self.cheese:
            self.trap = new_x, new_y
        else:
            self.trap = self.trap[0] + dx, self.trap[1] + dy

    def update_score(self, fake=False):
        # check for collisions
        pos = self.mouse
        if pos == self.cheese: # yay we got the cheese, score goes up
            self.cheese = self.random_location()
            if fake: return 1
            self.score += 1
        elif pos == self.trap and not self.easy:
            self.trap = self.random_location()  # reset the trap
            self.mouse = self.random_location() # respawn the player
            self.score -= 1
            if fake: return -1
        if self.easy:
            self.trap = (-9, -9)
        if fake: return 0

    def random_location(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        while ((x,y) == self.mouse or (x,y) == self.cheese or (x,y) == self.trap):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

        return x, y

    def get_relative_location(self, item):
        """Gets the relative location of the item to the mouse.
        Resulting coordinates x,y are in the range [-(width-1)/2,width/2]
         and [-(height-1)/2,height/2] and signify how far the item is
         in front and to the right of the mouse."""
        # print 'get_relative_location ', item, self.mouse

        # get object relative to mouse
        item = (item[0] - self.mouse[0]), (item[1] - self.mouse[1])

        # rotate
        direction = self.direction
        if direction == 'up':
            angle = 0.0
        elif direction == 'right':
            angle = 90.0
        elif direction == 'down':
            angle = 180.0
        elif direction == 'left':
            angle = 270.0
        x, y = item
        xp = x * math.cos(math.radians(angle)) - y * math.sin(math.radians(angle))
        yp = x * math.sin(math.radians(angle)) + y * math.cos(math.radians(angle))
        item = int(round(xp)), int(round(yp))

        # normalize around mouse
        item = item[0] % self.width, item[1] % self.height
        x = item[0] if item[0] <= self.width / 2 else item[0] - self.width
        y = item[1] if item[1] <= self.height / 2 else item[1] - self.height
        # print 'get_relative_location ', (x,y)
        return x, y

class RidgeEnvironment(MouseEnvironment):
    def __init__(self, do_render=False):
        self.width = 6
        self.height = 3
        self.score = 0
        self.mouse = (0, 0)
        self.cheese = (5, 0)
        self.do_render = do_render
        self.suppressed = False
        if self.do_render:  #   BIG RED NOTICE HERE
            global pygame   # -----------------------
            global render   # Only import into global
            import pygame   #    namespace if the
            import render   #   render flag is set!
            pygame.init()
            self.r = render.Renderer(self.width, self.height)

    def set_size(self, w, h):
        self.width = w
        self.height = h
        self.cheese = (w-1, 0)
        if self.do_render:
            self.r = render.Renderer(self.width, self.height)


    def reset(self):
        self.score = 0
        self.mouse = (0, 0)
        self.cheese = (self.width-1, 0)
        
    def play(self, action):
        x, y = self.mouse
        if action == 'left':
            x = max(x-1, 0)
        elif action == 'right':
            x = min(x+1, self.width-1)
        elif action == 'up':
            y = max(y-1, 0)
        elif action == 'down':
            y = min(y+1, self.height-1)
#       print 'mouse was at {0}, and goes {2}'.format(self.mouse, 0, action),
        self.mouse = x, y
#       print '-> {0}'.format(self.mouse)
        # update score here because it's easy
        if y == 0 and (x > 0 and x < self.width-1): # death
            score = self.score
            self.reset()
            self.score = score - 1
        elif y == 0 and x == self.width-1:
            score = self.score
            self.reset()
            self.score = score + 1 # got the prize

    def render(self):
        if self.do_render:
            items = []
            for x in xrange(1, self.width):
                if x == self.width - 1:
                    color = render.YELLOW
                else:
                    color = render.RED
                loc = (x, 0)
                if color:
                    item = loc, color
                    items.append(item)
            mouse = self.mouse, render.WHITE
            items.append(mouse)
            self.r.render_custom(items, self.score)

