import learners
import agent

def train(agent):
    """This method should be implemented by the student"""
    print agent
    agent.set_epsilon(0.1)
    for i in xrange(30):
        agent.perform()

# select the agent here
def get_agent(game):
    actions = ['left', 'forward', 'right']
    player = agent.MetaAgent(game, actions, epsilon=0.1, fov=3, learner_class=learners.QLearn)
#   player = agent.Agent(game, actions, epsilon=0.1, fov=3)
    return player

