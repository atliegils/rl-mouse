import traceback
import agent
import evaluator
import summarizer

def train(agent):
    """This method should be implemented by the student"""
    print agent

# temporary method, maybe, we'll see
def get_agent():
    player = agent.MetaAgent(game, ['left', 'forward', 'right'], epsilon=0.1, fov=3)
    return player

def main():
    global args # this line does nothing, args is already in the global namespace
    # game and agent setup code
    g_actions = ['left', 'forward', 'right']
    game = Game()
    game.set_size(args.grid_size, args.grid_size)
    agent = get_agent()
    # train the agent
    train(agent)
    # turn off exploration
    agent.set_epsilon(0.0)
    # evaluate the training results
    file_name = evaluator.evaluate(agent)
    # print out a nice summary of how the evaluation went
    summarizer.summarize(file_name)


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
    except Exception:
        print '\nERROR'
        print 'traceback:'
        print traceback.print_exc()
        print 'message:'
        print e
        


