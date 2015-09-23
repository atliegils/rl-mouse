import math, random
import time, traceback
from game import Game
from learners import HistoryManager, SARSA

# CAT, CHEESE AND TRAP AGENT
class Agent:
    def __init__(self, game):
        self.game = game
        self.score = 0

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

# Agent that tracks history
class HistoricalAgent(Agent):
    def __init__(self, game, actions, num_history_steps=2, epsilon=0.1, fov=3):
        self.learners = []
        self.game = game
        self.score = 0
        self.fov = fov
        self.create_learners(num_history_steps, epsilon, actions)
        self.cr = 5
        self.tr = 10
        self.hr = 1

    def adjust_rewards(self, cr, tr, hr):
        self.cr = cr
        self.tr = tr
        self.hr = hr

    def create_learners(self, levels, epsilon, actions):
        bottom_level = HistoryManager(epsilon)
        bottom_level.history_learner = SARSA(actions, epsilon)
        bottom_level.left_learner = SARSA(actions, epsilon)
        top = bottom_level
        for i in range(levels-1):
            top.q = self.default_q()
            next_level = HistoryManager(epsilon)
            next_level.left_learner = SARSA(actions, epsilon)
            next_level.history_learner = top
            top = next_level
        self.main_learner = top
        self.register_learners()

    def register_learners(self):
        top = self.main_learner
        while top:
            try:
                if top.left_learner:
                    self.learners.append(top.left_learner)
            except AttributeError:
                self.learners.append(top) # top doesn't have a left learner because it's SARSA
                break
            try:
                top = top.history_learner
            except AttributeError:
                break
        for ll in self.learners:
            print 'registered learner {0}'.format(ll)
        return # done, we hit a dead end

    def perform(self, verbose=0):
        self.verbose = verbose
        state_now = self.get_fov(self.fov)
        self.main_learner.set_state(state_now) # sets all states
        final_action = self.decide(self.main_learner) # selects recursively
        if verbose == 3:
            print 'mouse is facing {0} with state {1}'.format(self.game.direction, state_now)
            self.game.render()
            c = raw_input('continue...')
        self.game.play(final_action)
        reward = self.check_reward()
        if reward == 1:
            value = self.cr
        elif reward == -1:
            value = -self.tr
        else:
            value = -self.hr
        self.reward(value)
        return reward

    # deciding for top (main) learner
    def decide(self, choice):
        self.selections = []
        learner = self.main_learner
        decision = self._decide(learner)
        if self.verbose == 3: print ''
#       unselected = [x for x in self.learners if x not in self.selections]
#       for ll in unselected:
        for ll in self.learners:
            ll.update_action(decision)
            if self.verbose == 3:
                print '{0} - {1} - {2} - {3} // {4}'.format(ll.last_state, ll.current_state, ll.last_action, ll.current_action, ll)
        return decision

    def _decide(self, learner):
        choice = learner.select()
        if self.verbose == 3:
#           print '{0} selected {1}'.format(learner, choice)
            print ' -> {0}'.format(choice),
        if choice == 'now':
            new_learner = learner.left_learner
        elif choice == 'next':
            new_learner = learner.history_learner
        else: # final choice
            return choice
        self.selections.append(learner)
        return self._decide(new_learner)

    def reward(self, value):
        for s in self.selections:
            s.learn(value)
            if self.verbose == 3 and value != -2:
                from pprint import pprint
                print 'Q-matrix of {0}:'.format(s)
                pprint(s.q)
                print 'H{0} rewarded with {1}.'.format(s, value)
        self.selections = []
        for s in self.learners:
            if 'forward' in s.actions:
                s.learn(value)
                if self.verbose == 3 and value != -2:
                    from pprint import pprint
                    print 'Q-matrix of {0}:'.format(s)
                    pprint(s.q)
                    print 'S{0} rewarded with {1}.'.format(s, value)

    def default_q(self):
        d = {(0,0): {'now': -5.0, 'next': 10.0}}
        return {}
        return d

