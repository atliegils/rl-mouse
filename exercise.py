import learners
import agent

# train the agent before evaluation
def train(agent):
    """This method should be implemented by the student
    An example implementation is provided."""
    print 'Training {0}...'.format(agent)
    agent.set_epsilon(0.1)  # set the exploration
    for i in xrange(3000):  # train it for 1000 steps
        agent.perform()     # do an action

# select the agent here
def get_agent(game):
    actions = ['left', 'forward', 'right']
    player = agent.MetaAgent(game, actions, epsilon=0.1, fov=3, learner_class=learners.QLearn)
#   player = agent.Agent(game, actions, epsilon=0.1, fov=3)
    return player

