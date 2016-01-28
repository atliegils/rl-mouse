import random

class NotImplementedException(Exception):
    pass

### Base learner class
class BaseLearner:
    def __init__(self, actions, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9):
        self.q = {}
        self.exploration_rate = exploration_rate
        self.learning_rate    = learning_rate
        self.discount_factor  = discount_factor
        self.actions = actions
        self.last_reward = 0
        self.last_action = None
        self.last_state  = None
        self.current_action = None
        self.current_state  = None

    def dump_policy(self, dest):
#       import pickle
        from pprint import pprint
        try:
            import os
            target_path = 'policies'
            os.makedirs(target_path)
        except OSError as e: # silently ignore any errors, other errors _will_ appear if this fails
            import errno
            if e.errno == errno.EEXIST and os.path.isdir(target_path):
                pass
            else: raise
        with open('policies/' + dest + '.qtable', 'w') as f:
#           pickle.dump(self.q, f)
            pprint(self.q, stream=f)
        policy = {}
        for state, val in self.q.iteritems():
            actions = val.keys()
            qs = val.values()
            policy[state] = actions[qs.index(max(qs))]
        with open('policies/' + dest + '.policy', 'w') as f:
#           pickle.dump(policy, f)
            pprint(policy, stream=f)

    # sets the current state of the learner and updates the last state and action
    def set_state(self, state):
        self.last_state     = self.current_state
        self.last_action    = self.current_action
        self.current_state  = state
        self.current_action = None

    # helper function for default (uninitialized) values
    def get_default_row(self):
        row = {}
        for act in self.actions:
            row[act] = 0.0
        return row

    # Q-matrix accessor
    def getQ(self, state, action):
        row = self.q.get(state, self.get_default_row())
        return row.get(action, 0.0)

    # internal method for updating the Q-matrix (dictionary is this implementation)
    def learnQ(self, state, action, reward, maxqnew):
        if state is None:
            return # don't learn anything yet
        oldv = self.getQ(state, action)
        row = self.q.get(state, self.get_default_row())
        value = reward + self.discount_factor * maxqnew
        row[action] = oldv + self.learning_rate * (value - oldv)
        self.q[state] = row

    # Should be implemented in subclasses
    def learn(self, *args):
        raise NotImplementedException('BaseLearner::learn({0})'.format(args))

    # shorthand for set_state(state);select()
    def sselect(self, state):
        self.set_state(state)
        return self.select()

    # sets the current action without selection (someone else made this decision)
    def update_action(self, action):
        self.current_action = action

    # select an action based on the current state of the learner
    def select(self):
        state = self.current_state
        if random.random() < self.exploration_rate:
            action = random.choice(self.actions)
        else:
            vals = [self.getQ(state, a) for a in self.actions]
            maxQ = max(vals)
            count = vals.count(maxQ)
            if count > 1:
                best = [i for i in range(len(self.actions)) if vals[i] == maxQ]
                i = random.choice(best)
            else:
                i = vals.index(maxQ)
            action = self.actions[i]
        self.current_action = action
        return action
     
    def update_actions(self, action):
        self.update_action(action)
        

# Q-learners always expect the best possible outcome -- good for offline agents
class QLearn(BaseLearner):
    def learn(self, reward, next_state):
        maxqnew = max([self.getQ(next_state, a) for a in self.actions]) if next_state is not None else 0
        self.learnQ(self.current_state, self.current_action, reward, maxqnew)

# Note: not using softmax
class QPLearn(QLearn):
    # select an action based on the current state of the learner
    def select(self):
        def weighted_selection(items):
            def normalize(items):
                low_bound = min(items)
                items = [x - low_bound for x in items]
                return items
            items = normalize(items)
            r = random.uniform(0, sum(items))
            s = 0.0
            for i, weight in enumerate(items):
                s += weight
                if r < s: return i
            return i
        # select(self)
        state = self.current_state
        if random.random < self.exploration_rate:
            action = random.choice(self.actions)
        else:
            vals = [self.getQ(state, a) for a in self.actions]
            selection = weighted_selection(vals)
#           print 'selected {0} from {1} ({2})'.format(selection, vals, self.actions[selection])
            action = self.actions[selection]
        self.current_action = action
        return action

# SARSA learners learn from 'experiences' -- good for online agents
class SARSA(BaseLearner):
    def learn(self, reward, next_state):
        if self.current_action and self.last_action and self.current_state is not None and self.last_state is not None:
            qnext = self.getQ(self.current_state, self.current_action)
            self.learnQ(self.last_state, self.last_action, self.last_reward, qnext)
        # else:
        #     print 'foo: {0} {1} {2} {3} {4}'.format(self, self.last_state, self.current_state, self.last_action, self.current_action)
        if next_state is None: # terminal state
            self.learnQ(self.current_state, self.current_action, reward, 0)
            self.current_state = None
            self.current_action = None
        self.last_reward = reward

# Learner that optionally selects its action based on a past state
class HistoryManager(BaseLearner):

    def __init__(self, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9):
        self.q = {}
        self.exploration_rate = exploration_rate
        self.learning_rate   = learning_rate
        self.discount_factor   = discount_factor
        self.last_reward = 0
        self.last_action = None
        self.last_state  = None
        self.current_action = None
        self.current_state  = None
        self.left_learner = None
        self.history_learner = None
        self.actions = ['now', 'next']

    def set_state(self, state):
        self.left_learner.set_state(state)
        if self.current_state:
            self.history_learner.set_state(self.current_state)
        self.last_state     = self.current_state
        self.last_action    = self.current_action
        self.current_state  = state
        self.current_action = None

    def update_actions(self, action):
        self.left_learner.update_action(action)
        try:
            self.history_learner.update_actions(action)
        except:
            target = self.history_learner
            if target:
                target.update_action(action)
            else:
                print 'error'

    def learn(self, reward, next_state):
        if self.last_action:
            qnext = self.getQ(self.current_state, self.current_action)
            self.learnQ(self.last_state, self.last_action, self.last_reward, qnext)
        if next_state is None: # terminal state
            self.learnQ(self.current_state, self.current_action, reward, 0)
            self.current_state = None
            self.current_action = None
        self.last_reward = reward
        if self.current_action   == 'now':
            self.left_learner.learn(reward, next_state)
        elif self.current_action == 'next':
            self.history_learner.learn(reward, self.current_state if next_state is not None else None)
        else:
            raise Exception('Somehow neither learner was selected!')

    def printH(self, indent=0):
        def idd(indent, foo, a=''):
            for i in xrange(indent):
                print '|\t',
            print '-> {0} {1}'.format(foo, a)
        idd(indent, self, 'S')
        idd(indent+1, self.left_learner, 'L')
        if isinstance(self.history_learner, HistoryManager):
            self.history_learner.printH(indent+1)
        else:
            idd(indent+1, self.history_learner, 'H')

    def share_experience(self, reward, next_state):
        if isinstance(self.left_learner, HistoryManager): #? is this ever true?
            self.left_learner.share_experience(reward, next_state)
        else:
            self.left_learner.learn(reward, next_state)
        if isinstance(self.history_learner, HistoryManager):
            self.history_learner.share_experience(reward, self.current_state if next_state is not None else None)
        else:
            self.history_learner.learn(reward, self.current_state if next_state is not None else None)
                
# Meta learner that forms a tree structure of learners, rewarding an
class MetaLearner(BaseLearner):
    
    def __init__(self, left, right, exploration_rate=0.1, learning_rate=0.2, discount_factor=0.9):
        self.q = {}
        self.exploration_rate = exploration_rate
        self.learning_rate   = learning_rate
        self.discount_factor   = discount_factor
        self.side = ''
        self.last_reward = 0
        self.last_action = None
        self.last_state  = None
        self.current_action = None
        self.current_state  = None
        self.left_learner   = left
        self.right_learner  = right
        self.actions = [self.left_learner, self.right_learner]

    def set_state(self, state_left, state_right):
        if isinstance(self.left_learner, MetaLearner):
            self.left_learner.set_state(*state_left)
        else:
            self.left_learner.set_state(state_left)
        if isinstance(self.right_learner, MetaLearner):
            self.right_learner.set_state(*state_right)
        else:
            self.right_learner.set_state(state_right)
        self.last_state     = self.current_state
        self.last_action    = self.current_action
        if 'left' in self.side:
            self.current_state  = state_left
        elif 'right' in self.side:
            self.current_state  = state_right
        else: 
            self.current_state  = (state_left, state_right)
        self.current_action = None

    def learn(self, reward, next_states=None):
        # reward self
        qnext = self.getQ(self.current_state, self.current_action)
        if self.last_action:
            self.learnQ(self.last_state, self.last_action, self.last_reward, qnext)
        self.last_reward = reward
        # now teach children
        def apply_learn(learner, reward, used=False, next_state=None):
            """Apply learning to sub-learners"""     # avoid code duplication
            if hasattr(learner, 'share_experience'): # delegate reward
                learner.share_experience(reward, next_state)
            else:
                learner.learn(reward, next_state)

        apply_learn(self.left_learner, reward, used=(self.left_learner==self.current_action), next_state=next_states[0])
        apply_learn(self.right_learner, reward, used=(self.right_learner==self.current_action), next_state=next_states[1])

    def update_actions(self, action):
        self.left_learner.update_actions(action)
        self.right_learner.update_actions(action)

