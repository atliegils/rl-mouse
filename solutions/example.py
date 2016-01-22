import learners
import agent

# select the agent here
def get_agent(game):
    """Modify this method to create the appropriate agent"""
    actions = ['left', 'forward', 'right']
    # Use a MetaMouseAgent with QLearners at leaf nodes
    # player = agent.MetaMouseAgent(game, actions, exploration_rate=0.1, fov=3, learner_class=learners.QLearn)
    # Use a flat MouseAgent with the default SARSA learner
    player = agent.MouseAgent(game, actions, epsilon=0.1, fov=3)
    return player


# train the agent before evaluation
def train(player):
    """This method should be implemented by the student
    An example implementation is provided."""
    print 'Training...'
    player.set_exploration_rate(0.1)  # set the exploration
    for i in xrange(3000):   # train it for 3000 steps
        player.perform()     # do an action at every step
    player.set_exploration_rate(0.0) # turn off exploration if you're using on-policy learning

