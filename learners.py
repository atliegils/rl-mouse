import random

class NotImplementedException(Exception):
    pass

class BaseLearner:
    def __init__(self, actions, epsilon=0.1, alpha=0.2, gamma=0.8):
        self.q = {}
        self.epsilon = epsilon
        self.alpha   = alpha
        self.gamma   = gamma
        self.actions = actions
        self.last_reward = 0
        self.last_action = None
        self.last_state  = None
        self.current_action = None
        self.current_state  = None

    def set_state(self, state):
        self.last_state     = self.current_state
        self.last_action    = self.current_action
        self.current_state  = state
        self.current_action = None

    def get_default_row(self):
        row = {}
        for act in self.actions:
            row[act] = 0.0
        return row

    def getQ(self, state, action):
        row = self.q.get(state, self.get_default_row())
        return row.get(action, 0.0)

    def learnQ(self, state, action, reward, maxqnew):
        if state == None:
            return # don't learn anything yet
        oldv = self.getQ(state, action)
        row = self.q.get(state, self.get_default_row())
        value = reward + self.gamma * maxqnew
        row[action] = oldv + self.alpha * (value - oldv)
        self.q[state] = row

    def learn(self, *args):
        raise NotImplementedException('BaseLearner::learn({0})'.format(args))

    # shorthand for set_state(state);select()
    def sselect(self, state):
        self.set_state(state)
        return self.select()

    # sets the current action without selection (someone else made this decision)
    def update_action(self, action):
        self.current_action = action

    def select(self):
        state = self.current_state
        if random.random < self.epsilon:
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

class QLearn(BaseLearner):
    def learn(self, reward, next_state):
        maxqnew = max([self.getQ(next_state, a) for a in self.actions])
        self.learnQ(self.current_state, self.current_action, reward, maxqnew)

class SARSA(BaseLearner):
    def learn(self, reward):
        if self.current_action and self.last_action and self.current_state != None and self.last_state != None:
            qnext = self.getQ(self.current_state, self.current_action)
            self.learnQ(self.last_state, self.last_action, self.last_reward, qnext)
        else:
            print 'foo: {0} {1} {2} {3} {4}'.format(self, self.last_state, self.current_state, self.last_action, self.current_action)
        self.last_reward = reward

class HistoryManager(BaseLearner):

    def __init__(self, epsilon=0.1, alpha=0.2, gamma=0.8):
        self.q = {}
        self.epsilon = epsilon
        self.alpha   = alpha
        self.gamma   = gamma
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

    def learn(self, reward):
        qnext = self.getQ(self.current_state, self.current_action)
        if self.last_action:
            self.learnQ(self.last_state, self.last_action, self.last_reward, qnext)
        self.last_reward = reward
        if self.current_action   == 'now':
            self.left_learner.learn(reward)
        elif self.current_action == 'next':
            self.history_learner.learn(reward)
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

    def share_experience(self, reward):
        if isinstance(self.left_learner, HistoryManager):
            self.left_learner.share_experience(reward)
        else:
            self.left_learner.learn(reward)
        if isinstance(self.history_learner, HistoryManager):
            self.history_learner.share_experience(reward)
        else:
            self.history_learner.learn(reward)
                

class MetaLearner(BaseLearner):
    
    def __init__(self, left, right, epsilon=0.1, alpha=0.2, gamma=0.8):
        self.q = {}
        self.epsilon = epsilon
        self.alpha   = alpha
        self.gamma   = gamma
        self.last_reward = 0
        self.last_action = None
        self.last_state  = None
        self.current_action = None
        self.current_state  = None
        self.left_learner   = left
        self.right_learner  = right
        self.actions = [self.left_learner, self.right_learner]

    def set_state(self, state_left, state_right):
        self.left_learner.set_state(state_left)
        self.right_learner.set_state(state_right)
        self.last_state     = self.current_state
        self.last_action    = self.current_action
        self.current_state  = (state_left, state_right)
        self.current_action = None

    def learn(self, reward):
        qnext = self.getQ(self.current_state, self.current_action)
        if self.last_action:
            self.learnQ(self.last_state, self.last_action, self.last_reward, qnext)
        self.last_reward = reward
        # now reward children
        self.current_action.learn(reward)
        other = self.left_learner
        if self.current_action == self.left_learner:
            other = self.right_learner
        if isinstance(other, SARSA):
            other.learn(reward)
        else: # historical
            other.share_experience(reward)
