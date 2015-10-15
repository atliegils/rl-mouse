import learners
import agent

# select the agent here
def get_agent(game):
    """Modify this method to create the appropriate agent"""
    actions = ['left', 'forward', 'right']
    # Use a MetaAgent with QLearners at leaf nodes
    player = agent.MetaAgent(game, actions, epsilon=0.1, fov=3, learner_class=learners.QLearn)
    # Use a flat Agent with the default SARSA learner
#   player = agent.Agent(game, actions, epsilon=0.1, fov=3)
    return player


# train the agent before evaluation
def train(player):
    """This method should be implemented by the student
    An example implementation is provided."""
    print 'Training {0}...'.format(player)
    player.set_epsilon(0.1)  # set the exploration
    for i in xrange(3000):   # train it for 3000 steps
        player.perform()     # do an action at every step

# control over rewards for (finding cheese, entering a trap, walking)
# by default the rewards are scaled by [1, -1, -1]
def reward_profile(player):
    """The reward profile can be adjusted by changing the line below
    Hint: Flat learners sometimes require a little extra push --
    by punishing the learner every step it learns not to walk in circles"""
    player.adjust_reward(2,3,1)

