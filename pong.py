import math
import random

class Rectangle:
    def __init__(self, left, top, width, height):
        self.x = left
        self.y = top
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.topleft = top, left
        self.topright = top, left + width
        self.bottomleft = top + height, left
        self.bottomright = top + height, left + width

    def move(self, dx, dy):
        left = self.left + dx
        top = self.top + dy
        return Rectangle(left, top, self.width, self.height)

    def inflate(self, dx, dy):
        left = int(self.left - float(dx)/2)
        top = int(self.top - float(dy)/2)
        width = int(self.width + float(dx)/2)
        height = int(self.height + float(dy)/2)
        return Rectangle(left, top, width, height)

    def contains(self, rect):
        if rect.x < self.x: return False
        if rect.y < self.y: return False
        if rect.x + rect.width  > self.x + self.width: return False
        if rect.y + rect.height > self.y + self.height: return False
        return True


    def collidepoint(self, point):
        x,y = point
        if self.left < x and self.left + self.width >= x\
        and self.top < y and self.top + self.height >= y:
            return True
        return False

    def colliderect(self, rect):
        return self.x < rect.x + rect.width   \
            and self.x + self.width > rect.x  \
            and self.y < rect.y + rect.height \
            and self.y + self.height > rect.y

    def __repr__(self):
        return '({0}+{2}, {1}+{3})'.format(int(self.x), int(self.y), int(self.width), int(self.height))


class Pong:

    def __init__(self, do_render=True):
        self.area = Rectangle(0, 0, 640, 480)
        if do_render: 
            global pygame
            import pygame
#           from pygame.locals import *
            pygame.init()
            self.display = pygame.display.set_mode((self.area.width, self.area.height))
            pygame.display.set_caption('Pong')
#           self.clock = pygame.time.Clock()
        self.do_render = do_render
        self.render_time = 0.012
        self.scores = [0, 0]
        self.moved = False
        self.discrete = False
        self.paddles = [None, None]
        self.paddles[0] = self.Paddle('left', self.area)
        self.paddles[1] = self.Paddle('right', self.area)
        self.difficulty = 1
        self.serve()

    def reset(self, soft=False):
        if not soft:
            self.scores = [0, 0]
        self.moved = False
        self.paddles = [None, None]
        self.paddles[0] = self.Paddle('left', self.area)
        self.paddles[1] = self.Paddle('right', self.area)
        self.serve()

    def serve(self):
        angle = random.random() - 0.45
        speed = random.choice([9, -9])
        self.ball = self.Ball((angle, speed), Rectangle(self.area.width/2, self.area.height/2, 15, 15), self.area) #pygame.Rect(320, 240, 9, 9))

    def play_frame(self, action):
        self.move(action)
        self.move_auto(1)
        result = self.update_frame()
        return result

    def play(self, action=None):
        if action:
            return self.play_frame(action)
        else:
            raise Exception('Continuous play not allowed')

    # Returns the x/y coordinates of the ball and the y coordinate of the player's paddle
    def get_state(self):
        y_self = self.paddles[0].rect.y + self.paddles[0].rect.height / 2
        y_ball = self.ball.rect.y + self.ball.rect.height / 2
        x_ball = self.ball.rect.x + self.ball.rect.width / 2
        return y_self, y_ball, x_ball # Yp, Yb, Xb

    def update_frame(self):
#       for paddle in self.paddles:
#           paddle.update()
        winner = self.ball.update(self.paddles)
        if winner:
            self.scores[winner-1] += 1
            self.serve()
        self.render()
        return winner

    def move(self, action, index=0):
        if action == 'stop':
            self.paddles[index].movepos = [0, 0]
            self.paddles[index].state = 'still'
        elif action == 'up':
            self.paddles[index].moveup()
        elif action == 'down':
            self.paddles[index].movedown()
        elif action == 'auto':
            self.move_auto(index)

    def move_auto(self, index):
        # simple non-learning ai
        y_self = self.paddles[index].rect.y + self.paddles[index].rect.height/2
        y_ball = self.ball.rect.y + self.ball.rect.height/2
        if self.difficulty == 1:
            if random.random() > 0.55:
                self.move('stop')
                return
            elif random.random() < 0.45:
                self.move(random.choice(['stop', 'up', 'down']))
                return
        if y_ball == y_self:
            self.move('stop', index)
        elif y_ball < y_self:
            self.move('up', index)
        elif y_ball > y_self:
            self.move('down', index)


    def render(self):
        if not self.do_render:
            return
        def rectify(rect):
            return pygame.Rect(rect.left, rect.top, rect.width, rect.height)
        YELLOW = (255, 255, 000)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        self.display.fill(BLACK)
        pygame.draw.rect(self.display, YELLOW, rectify(self.ball.rect))
        for paddle in self.paddles:
            pygame.draw.rect(self.display, WHITE, rectify(paddle.rect))
        pygame.display.update()
        # unnecessary code: (replaces clock but delays more than just rendering)
        if self.render_time:
            import time
            time.sleep(self.render_time)


    class Ball:

        def __init__(self, vector, rect, area):
            self.vector = vector
            self.hit = 0
            self.rect = rect
#           self.area = pygame.display.get_surface().get_rect()
            self.area = area
            self.last_collision = -1

        def update(self, paddles):
            newpos = self.calcnewpos(self.rect, self.vector)
            (angle, z) = self.vector
            new_area = self.area.inflate(25,0)
            new_area = self.area # patch above line away... for now
#           print 'BALL:   {0}\nPADDLE: {1}\nPADDL2: {3} ; angle: {2} '.format(self.rect, paddles[0].rect, degrees(angle) , paddles[1].rect) # debug only
            if not new_area.contains(newpos):
                self.last_collision = -1
                if newpos.y < self.area.y or newpos.y + newpos.height > self.area.y + self.area.height:
                    angle = -angle
                elif self.rect.x + self.rect.width < new_area.x:
                    return 2
                elif self.rect.x > new_area.x + new_area.width:
                    return 1
            for idx, paddle in enumerate(paddles):
                if self.rect.colliderect(paddle.rect) and idx != self.last_collision:
                    angle = (math.pi - angle)
                    angle = angle + random.choice([random.random() / 0.9, -random.random() / 0.9])
                    newpos = self.calcnewpos(self.rect, (angle, z))
                    self.last_collision = idx
            self.rect = newpos
            self.vector = (angle, z)
            return 0

        def calcnewpos(self, rect, vector):
            (angle, z) = vector
            (dx, dy) = (z*math.cos(angle), z*math.sin(angle))
            return rect.move(dx, dy)

    class Paddle:

        def __init__(self, side, area):
#           self.area = pygame.display.get_surface().get_rect()
            self.area = area
            self.side = side
#           self.rect = pygame.Rect(5, 5, 10, 50)
            if self.side == 'left':
                side_val = 0
            elif self.side == 'right':
                side_val = area.width - 20
            self.rect = Rectangle(side_val, area.height/2, 20, 50)
            self.speed = 10
            self.state = 'still'

        def handicap(self, value):
            if self.side == 'left':
                side_val = 0
            elif self.side == 'right':
                side_val = self.area.width - 20
            self.rect = Rectangle(side_val, self.rect.y, 20, 50 + value)

        def moveup(self):
            rect = self.rect.move(0, -self.speed)
            if self.area.contains(rect):
                self.rect = rect
            self.state = 'moveup'

        def movedown(self):
            rect = self.rect.move(0,  self.speed)
            if self.area.contains(rect):
                self.rect = rect
            self.state = 'movedown'

if __name__ == '__main__':
    p = Pong()
    p.difficulty = 123
    winner = 0
    try:
        for x in xrange(100):
            while not winner:
                p.play('auto')
    except KeyboardInterrupt:
        print 'exiting...'

