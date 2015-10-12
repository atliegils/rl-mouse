import argparse
import traceback
import learners
import agent
import evaluator
import summarizer
from game import Game

def train(agent):
    """This method should be implemented by the student"""
    print agent
    agent.set_epsilon(0.1)
    for i in xrange(3):
        agent.perform()

# temporary method, maybe, we'll see
def get_agent(game):
    actions = ['left', 'forward', 'right']
    player = agent.MetaAgent(game, actions, epsilon=0.1, fov=3, learner_class=learners.QLearn)
#   player = agent.Agent(game, actions, epsilon=0.1, fov=3)
    return player

def main():
    global args # this line does nothing, args is already in the global namespace
    # game and agent setup code
    game = Game()
    game.set_size(args.grid_size, args.grid_size)
    agent = get_agent(game)
    agent.adjust_rewards(2,3,1)
    agent.game.suppressed = True
    # train the agent
    train(agent)
    # clean up after training
    agent.accumulated = 0  # reset accumulated rewards
    agent.set_epsilon(0.0) # turn off exploration
    # evaluate the training results
    file_name = evaluator.evaluate(agent)
    # print out a nice summary of how the evaluation went
    summarizer.summarize_e(file_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RL Learner exercise')
    parser.add_argument('-g', '--grid_size', type=int, default=7, help='grid size')
    args = parser.parse_args()
    try:
        main()
        exit(0)
    except SystemExit:
        exit(1)
    except KeyboardInterrupt:
        print 'CTRL + C detected, canceling...'
        exit(0)
    except Exception, e:
        print '\nERROR'
        print 'traceback:'
        print traceback.print_exc()
        print 'message:'
        print e
        


