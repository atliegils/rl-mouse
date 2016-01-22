import math
from learners import HistoryManager, SARSA, MetaLearner, QLearn

class BaseAgent(object):
    def __init__(self, game, actions, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9, learner_class=SARSA):
        self.game = game
        self.score = 0
        self.accumulated = 0
        self.learner_class = learner_class
        self.learner = learner_class(actions, exploration_rate, learning_rate=learning_rate, discount_factor=discount_factor)
        self.learning = True

    def replace_actions(self, actions):
        self.learner = self.learner_class(actions, self.learner.exploration_rate)

    def set_exploration_rate(self, exploration_rate):
        self.learner.exploration_rate = exploration_rate

    def decide(self, learner):
        return learner.select()

    def set_state(self, state):
        self.state = state

    def modify_state(self, state):
        return state


# CAT, CHEESE AND TRAP AGENTS
class MouseAgent(BaseAgent):
    def __init__(self, game, actions, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9, fov=2, learner_class=SARSA):
        super(MouseAgent, self).__init__(game, actions, exploration_rate=exploration_rate, learning_rate=learning_rate, discount_factor=discount_factor, learner_class=learner_class)
        self.fov = fov
        self.adjust_rewards( 1,  1,  0 )
        self.reward_scaling([1, -1, -1])
        self.dephased = False

    def adjust_rewards(self, cr, tr, hr):
        self.cr = cr
        self.tr = tr
        self.hr = hr

    def reward_scaling(self, arr):
        self.scaling = arr

    def is_hunger(self, value):
        scaling_factor = float(self.game.width + self.game.height) / 2
        if self.cr * self.scaling[0] == value \
        or self.tr * self.scaling[1] == value:
            return False
        if float(self.hr * self.scaling[2]) / scaling_factor == value:
            return True
        print 'wow what happened in is_hunger? value was ', value
        return False

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
        x = (x + self.game.width) % self.game.width
        y = (y + self.game.height) % self.game.height
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
        if self.dephased:
            return traps, cheese
        return cheese, traps

    def check_outcome(self):
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

    def reward(self, value):
        if not self.is_hunger(value):
            self.accumulated += value
        if not self.learning: return
        if isinstance(self.learner, QLearn): # provide next state for Q-Learners
            self.learner.learn(value, self.modify_state(self.get_fov(self.fov)))
        else:
            self.learner.learn(value)

    def perform(self, explore=True, last_action=True, verbose=0):
        self.verbose = verbose
        state_now = self.get_fov(self.fov)
        if explore:
            explo = self.get_fov(self.fov*2)
            state_now = state_now + (explo[0] + explo[1],)
        if last_action:
            state_now = state_now + (self.learner.current_action,)
        self.learner.set_state(self.modify_state(state_now)) # sets all states
        final_action = self.decide(self.learner)
        self.game.play(final_action)
        outcome = self.check_outcome() # 1=positive, -1=negative, 0=neutral
        reward = self.calc_reward(outcome)
        self.reward(reward)
        return outcome

    def calc_reward(self, outcome):
        scaling_factor = float(self.game.width + self.game.height) / 2
        if outcome == 1:
            reward = self.scaling[0] * abs(self.cr)
        elif outcome == -1:
            reward = self.scaling[1] * abs(self.tr)
        else:
            reward = float(self.scaling[2] * abs(self.hr)) / scaling_factor
        return reward

    # This __ONLY__ exists for monkey patching perform more easily
    def modify_state(self, state):
        return state

class OmniscientMouseAgent(MouseAgent):
    def __init__(self, game, actions, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9, learner_class=SARSA):
        super(OmniscientMouseAgent, self).__init__(game, actions, exploration_rate=exploration_rate, learning_rate=learning_rate, discount_factor=discount_factor, fov=-1, learner_class=learner_class)

    def perform(self, explore=False, last_action=False, verbose=0):
#       return MouseAgent.perform(explore, last_action, verbose)
        return super(OmniscientMouseAgent, self).perform(explore, last_action, verbose)

    def modify_state(self, state):
        return state # fov
        # example usage of this method:
        def convert(item): # function to convert items into a standardized format
            if not item: return '0'
            return item[0]
        state_string = ''.join([convert(item) for sublist in state for item in sublist])
        raw_input(state_string)
        return state_string

    def get_fov(self, *args):
        # can always view the cheese and the trap objects
        # objects are relative to the mouse
        # all coordinates are >= 0 so that they indicate how far the object is
        # in front and to the right of the mouse (the grid is circular though)
        cx, cy = self.game.get_relative_location(self.game.cheese)
        tx, ty = self.game.get_relative_location(self.game.trap)
        if cx < 0:
            cx = self.game.width + cx
        if cy < 0:
            cy = self.game.height + cy
        if tx < 0:
            tx = self.game.width + tx
        if ty < 0:
            ty = self.game.height + ty
        return cx, cy, tx, ty

class DeterministicMouseAgent(OmniscientMouseAgent):
    def __init__(self, game, actions):
        super(DeterministicMouseAgent, self).__init__(game, actions, learner_class=QLearn)
        self.policy = {}

    def perform(self, explore=False, last_action=False, verbose=0):
        self.verbose = verbose
        state_now = self.get_fov(self.fov)
        #print state_now
        if last_action:
            state_now = state_now + (self.learner.current_action,)
        self.learner.set_state(self.modify_state(state_now)) # sets all states
        #final_action = self.decide(self.learner)
        final_action = self.policy.get(state_now, self.learner.actions[0])
        # print final_action
        self.game.play(final_action)
        outcome = self.check_outcome() # 1=positive, -1=negative, 0=neutral
        reward = self.calc_reward(outcome)
        self.reward(reward)
        return outcome

# Like a regular agent, but instead of seeing a cone, it sees a square around it
# uses omniscient agent state space logic
class RadiusMouseAgent(MouseAgent):
    def __init__(self, game, actions, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9, learner_class=SARSA, fov=2):
        super(RadiusMouseAgent, self).__init__(game, actions, exploration_rate=exploration_rate, learning_rate=learning_rate, discount_factor=discount_factor, learner_class=learner_class, fov=fov)

    def get_fov(self, radius=3):
        m_loc = self.game.mouse
        cheese = (self.game.cheese[0] - m_loc[0] + self.game.width) % self.game.width, (self.game.cheese[1] - m_loc[1] + self.game.height) % self.game.height
        # get trap relative to mouse
        trap = (self.game.trap[0] - m_loc[0] + self.game.width) % self.game.width, (self.game.trap[1] - m_loc[1] + self.game.height) % self.game.height
        # now rotate cheese and trap around the origin depending on direction
        # also remove things that are out of range
        def rotate_and_mask(item, angle):
            x,y = item
            xp = x * math.cos(math.radians(angle)) - y * math.sin(math.radians(angle))
            yp = x * math.sin(math.radians(angle)) + y * math.cos(math.radians(angle))
#           print '{0}R, xy {1} {2}; dxdy {3} {4}'.format(radius, x, y, xp, yp)
            # if the item is out of our view, we don't see it
            if abs(xp) > radius or abs(yp) > radius:
                return 0,0
            return int(xp), int(yp)
        direction = self.game.direction
        if direction == 'up':
            angle = 0.0
        elif direction == 'right':
            angle = 90.0
        elif direction == 'down':
            angle = 180.0
        elif direction == 'left':
            angle = 270.0
        # return the location of visible items, or (0,0) for any item that is not visible
        return rotate_and_mask(cheese, angle), rotate_and_mask(trap, angle)

        def modify_state(self, state):
            return state

# example utility class (extend this for debugging!)
class TraceMouseAgent(MouseAgent):
    def decide(self, learner):
        action = learner.select()
        print 'selected action {0}'.format(action)
        return action

# just wraps a learner in an agent so that it can perform
class WrapperMouseAgent(MouseAgent):
    def __init__(self, learner, game, fov):
        super(WrapperMouseAgent, self).__init__(game, [], fov=fov)
        self.learner = learner

    def perform(self, explore=False, last_action=False, verbose=0):
        self.verbose = verbose
        state_now = self.get_fov(self.fov)
        if explore:
            explo = self.get_fov(self.fov*2) # changed from 3 to 2
            state_now = state_now + (explo[0] + explo[1],)
        if last_action:
            state_now = state_now + (self.learner.current_action,)
        self.learner.set_state(self.modify_state(state_now)) # sets all states
        final_action = self.decide(self.learner) 
        self.game.play(final_action)
        outcome = self.check_outcome()
        reward = self.calc_reward(outcome)
        self.reward(reward)
        return outcome

# MouseAgent that tracks history
class HistoricalMouseAgent(MouseAgent):
    def __init__(self, game, actions, levels=2, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9, learner_class=SARSA, fov=2):
        super(HistoricalMouseAgent, self).__init__(game, actions, exploration_rate=exploration_rate, learning_rate=learning_rate, discount_factor=discount_factor, learner_class=learner_class, fov=fov)
        self.learners = []
        self.learner = None
        self.create_learners(levels, exploration_rate, actions)
        self.levels=levels
        self.cr = 5
        self.tr = 10
        self.hr = 1

    def replace_actions(self, actions):
        self.create_learners(self.levels, self.exploration_rate, actions)

    def set_exploration_rate(self, exploration_rate):
        def set_exploration_rate(learner, exploration_rate):
            left = learner.left_learner
            right = learner.history_learner
            if left:
                set_exploration_rate(left, exploration_rate)
            if right:
                set_exploration_rate(right, exploration_rate)
            learner.exploration_rate = exploration_rate
        set_exploration_rate(self.main_learner, exploration_rate)

    def create_learners(self, levels, exploration_rate, actions):
        bottom_level = HistoryManager(exploration_rate)
        bottom_level.history_learner = self.learner_class(actions, exploration_rate)
        bottom_level.left_learner = self.learner_class(actions, exploration_rate)
        top = bottom_level
        for i in range(levels-1):
            top.q = {}
            next_level = HistoryManager(exploration_rate)
            next_level.left_learner = self.learner_class(actions, exploration_rate)
            next_level.history_learner = top
            top = next_level
        self.main_learner = top
        self.register_learners()
        self.main_learner.printH()

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
        if not self.is_hunger(value):
            self.accumulated += value
        if not self.learning: return
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

class MetaMouseAgent(MouseAgent):
    def __init__(self, game, actions, levels=2, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9, learner_class=SARSA, fov=2):
        super(MetaMouseAgent, self).__init__(game, actions, exploration_rate=exploration_rate, learning_rate=learning_rate, discount_factor=discount_factor, learner_class=learner_class, fov=fov)
        left  = learner_class(actions, exploration_rate)
        right = learner_class(actions, exploration_rate)
        self.learner = MetaLearner(left, right, exploration_rate, learning_rate=learning_rate, discount_factor=discount_factor)

    def replace_actions(self, actions):
        left = self.learner_class(actions, self.exploration_rate)
        right = self.learner_class(actions, self.exploration_rate)
        self.learner = MetaLearner(left, right, self.exploration_rate, self.learning_rate, self.discount_factor)

    def set_exploration_rate(self, exploration_rate):
        def set_exploration_rate(learner, exploration_rate):
            if hasattr(learner, 'left_learner'):
                set_exploration_rate(learner.left_learner, exploration_rate)
            if hasattr(learner, 'right_learner'):
                set_exploration_rate(learner.right_learner, exploration_rate)
            learner.exploration_rate = exploration_rate
        set_exploration_rate(self.learner, exploration_rate)

    def set_states(self, last_action=False):
        # active state
        state_left = self.get_fov(self.fov)
        # exploration state
        state_right = self.get_fov(self.fov*2) # changed to 2
        if not self.game.easy: # if easy, then exploration is just better range...
            state_right = state_right[0] + state_right[1] # don't distinguish between items
        if last_action:
            state_right = (state_right, self.learner.right_learner.current_action)

        self.learner.set_state(state_left, state_right) # sets all states

    def perform(self, explore=True, last_action=True, verbose=0):
        self.verbose = verbose
        self.set_states(last_action)
        final_action = self.decide(self.learner) # selects recursively
        self.learner.left_learner.update_actions(final_action)
        self.learner.right_learner.update_actions(final_action)
        if verbose == 3:
            print 'mouse is facing {0} with state {1}'.format(self.game.direction, (state_left, state_right))
            self.game.render()
            c = raw_input('continue...')
        self.game.play(final_action)
        outcome = self.check_outcome()
        reward = self.calc_reward(outcome)
        self.next_states = (self.get_fov(self.fov), self.get_fov(self.fov*2))
        self.reward(reward)
        return outcome

    # deciding for top (main) learner
    def decide(self, choice):
        self.selections = []
        learner = self.learner
        decision = self._decide(learner)
        return decision

    def _decide(self, learner):
        choice = learner.select()
        if self.verbose == 3:
            print ' -> {0}'.format(choice),
        if choice in [self.learner.left_learner, self.learner.right_learner]:
            return self._decide(choice) # meta choice
        elif choice == 'now': # history choice
            new_learner = learner.left_learner
        elif choice == 'next':
            new_learner = learner.history_learner
        else: # final choice
            return choice
        self.selections.append(learner)
        return self._decide(new_learner)

    def reward(self, value):
        if not self.is_hunger(value):
            self.accumulated += value
        if not self.learning: return
        self.learner.learn(value, self.next_states)

# Like MetaMouseAgent, but set the state of the top level agent to 1/0 depending on if it can see cheese
class CheeseMeta(MetaMouseAgent):
    def set_states(self, last_action=False):
        # active state
        state_left = self.get_fov(self.fov)
        # exploration state
        state_right = self.get_fov(self.fov*2)
        if not self.game.easy: # if easy, then exploration is just better range...
            state_right = state_right[0] + state_right[1] # don't distinguish between items
        if last_action:
            state_right = (state_right, self.learner.right_learner.current_action)
        self.learner.set_state(state_left, state_right)
        self.learner.current_state = 0
        if state_left[0] or state_left[1]:
            self.learner.current_state = 1

    def decide(self, choice):
        self.selections = []
        if self.learner.current_state == 0:
            decision = self._decide(self.learner.right_learner)
        else:
            decision = self._decide(self.learner.left_learner)
        return decision

class RidgeAgent(MouseAgent):
    def __init__(self, game, actions, exploration_rate=0.1, discount_factor=0.995, learning_rate=0.1, learner_class=SARSA):
        super(RidgeAgent, self).__init__(game, actions, exploration_rate=exploration_rate, learning_rate=learning_rate, discount_factor=discount_factor, learner_class=learner_class)

    def perform(self):
        state_now = self.game.mouse
        self.learner.set_state(self.modify_state(state_now)) # sets all states
        final_action = self.decide(self.learner)
        self.game.play(final_action)
        outcome = self.check_outcome() # 1=positive, -1=negative, 0=neutral
#       print '{} -> {} -> {}'.format(state_now, final_action, reward)
        reward = self.calc_reward(outcome)
        self.reward(reward)
        return outcome

    def is_hunger(self, value):
        # disabled for this environment
        return False
        
    def calc_reward(self, outcome):
        if outcome == 0:
            return self.scaling[2] * abs(self.hr) # no scaling
        return super(RidgeAgent, self).calc_reward(outcome)

    def get_fov(self, fov):
        return self.game.mouse

    def decide(self, learner):
        selection = learner.select()
        return selection

class DeterministicRidgeAgent(RidgeAgent):
    def __init__(self, game, actions):
        super(DeterministicRidgeAgent, self).__init__(game, actions, learner_class=QLearn)

    def __init__(self, game, actions):
        self.fov = -1
        self.policy = {}

    def perform(self, explore=False, last_action=False, verbose=0):
        self.verbose = verbose
        state_now = self.get_fov(self.fov)
        #print state_now
        if last_action:
            state_now = state_now + (self.learner.current_action,)
        self.learner.set_state(self.modify_state(state_now)) # sets all states
        #final_action = self.decide(self.learner)
        final_action = self.policy.get(state_now, self.learner.actions[0])
        # print final_action
        self.game.play(final_action)
        outcome = self.check_outcome() # 1=positive, -1=negative, 0=neutral
        reward = self.calc_reward(outcome)
        self.reward(reward)
        return outcome

