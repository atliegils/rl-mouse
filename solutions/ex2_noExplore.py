import learners
import agent

# select the agent here
def get_agent(game):
    """Modify this method to create the appropriate agent"""
    actions = ['left', 'forward', 'right']
    player = agent.OmniscientMouseAgent(game, actions, learner_class=learners.QLearn)
    return player


# train the agent before evaluation
def train(player):
    """This method should be implemented by the student
    An example implementation is provided."""
    print 'Training...'
    player.set_exploration_rate(0.0)  # set the exploration
    for i in xrange(1000):  # train it for 1000 steps
        player.perform()     # do an action at every step
    player.set_exploration_rate(0.0) # turn exploration off for evaluation

