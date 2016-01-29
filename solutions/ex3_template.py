import learners
import agent

# select the agent here
def get_agent(game):
    """Modify this method to create the appropriate agent"""
    actions = ['left', 'forward', 'right']

    player = agent.MouseAgent(game, actions, learner_class=learners.QLearn)

    # player = agent.RadiusMouseAgent(game, actions, learner_class=learners.QLearn)

    # To create a custom FOV, edit the string that defines custom_fov below.
    # These examples show how you could have created the cone and radius. Spaces are not observed, 'x's (and other
    # characters) are observed, and the '^' specifies the agent's location and viewing direction.
    # # cone_fov = agent.FOV("""
    # #         xxxxx
    # #         xxxxx
    # #          xxx
    # #          xxx
    # #          x^x""")
    # # radius_fov = agent.FOV("""
    # #          xxx
    # #         xxxxx
    # #         xx^xx
    # #         xxxxx
    # #          xxx
    # #     """)
    # custom_fov = agent.FOV("""
    #      ^
    # """)
    # player = agent.CustomMouseAgent(game, actions, custom_fov, learner_class=learners.QLearn)

    return player


# train the agent before evaluation
def train(player):
    """This method should be implemented by the student
    An example implementation is provided."""
    print 'Training {0}...'.format(player)
    player.set_exploration_rate(0.25)  # set the exploration
    for i in xrange(1000):  # train it for N steps
        player.perform()     # do an action at every step
    player.set_exploration_rate(0.0)  # set the exploration
