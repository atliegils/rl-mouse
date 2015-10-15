#!/usr/bin/python2
import argparse
import agent
import copy
import evaluator
import learners
import summarizer
import traceback
from game import Game
from plotter import evaluation_plot, compare_evals

def comparison():
    e1 = evaluate(args.solution_name)
    e2 = evaluate(args.compare_to)
    compare_evals(e1, e2)

def evaluate(name):
    # import the solution name into the global namespace as 'exercise'
    exercise = __import__(name.rstrip('.py'))
    # game and agent setup code
    game = Game(do_render=False)
    game.set_size(args.grid_size, args.grid_size)
    original_game = copy.copy(game)
    # fetch the agent from the provided solution
    agent = exercise.get_agent(game)
    agent.adjust_rewards( 2,  3,  1 )
    agent.reward_scaling([1, -1, -1])
    agent.fov = args.fov
    agent.game.suppressed = True
    # train the agent using the provided solution
    exercise.train(agent)
    # clean up after training
    agent.accumulated = 0   # reset accumulated rewards
    agent.set_epsilon(0.0)  # turn off exploration
    agent.game.reset()      # reset the game
    agent.game.high_score = 0
    agent.fov = args.fov
    agent.game = original_game # if the training modifies the game, it is fixed here
    # evaluate the training results
    file_name = evaluator.evaluate(agent, name='eval_'+name) 
    # print out a nice summary of how the evaluation went
    summarizer.summarize_e(file_name)
    return file_name

def main():
    file_name = evaluate(args.solution_name)
    evaluation_plot(file_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RL Learner exercise')
    parser.add_argument('solution_name', default='exercise', nargs='?', help='exercise to evaluate')
    parser.add_argument('-c', '--compare_to', help='compare two solutions')
    parser.add_argument('-g', '--grid_size', type=int, default=7, help='grid size')
    parser.add_argument('-f', '--fov', type=int, default=3, help='base field of view')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    try:
        if args.debug:
#           summarizer.summarize_e('evaluation.txt')
#           compare_evals('eval_exercise.txt', 'eval_ex2.txt')
            print 'args.debug'
            exit(0)
        if args.compare_to:
            comparison()
        else:
            main()
    except SystemExit:
        exit(1)
    except KeyboardInterrupt:
        print '\rCTRL + C detected, canceling...'
        exit(2)
    except Exception, e:
        print '\nERROR'
        print 'traceback:'
        print traceback.print_exc()
        print 'message:'
        print e
        


