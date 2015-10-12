#!/usr/bin/python2
import argparse
import traceback
import learners
import agent
import evaluator
import summarizer
from game import Game

def main():
    # game and agent setup code
    game = Game()
    game.set_size(args.grid_size, args.grid_size)
    agent = exercise.get_agent(game)
    agent.adjust_rewards(2,3,1)
    agent.game.suppressed = True
    # train the agent
    exercise.train(agent)
    # clean up after training
    agent.accumulated = 0  # reset accumulated rewards
    agent.set_epsilon(0.0) # turn off exploration
    # evaluate the training results
    file_name = evaluator.evaluate(agent)
    # print out a nice summary of how the evaluation went
    summarizer.summarize_e(file_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RL Learner exercise')
    parser.add_argument('solution_name', default='exercise', nargs='?', help='exercise to evaluate')
    parser.add_argument('-g', '--grid_size', type=int, default=7, help='grid size')
    args = parser.parse_args()
    # import the solution name into the global namespace as 'exercise'
    exercise = __import__(args.solution_name)
    try:
        main()
    except SystemExit:
        exit(1)
    except KeyboardInterrupt:
        print 'CTRL + C detected, canceling...'
        exit(2)
    except Exception, e:
        print '\nERROR'
        print 'traceback:'
        print traceback.print_exc()
        print 'message:'
        print e
        


