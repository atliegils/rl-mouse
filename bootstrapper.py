#!/usr/bin/python2
import argparse
import copy
import evaluator
import summarizer
import os, sys, traceback
from game import Game
from plotter import evaluation_plot, compare_evals, counter_plot
from  functools import partial

def comparison():
    e1 = evaluate(args.solution_name)
    e2 = evaluate(args.compare_to)
    compare_evals(e1, e2)

def convert(name):
    return name.rstrip('.py').replace('/','.').replace('solutions.','')

def custom_training(agent):
    agent.set_epsilon(0.1)
    for i in xrange(args.custom_training):
        agent.perform()

def fetch_agent(exercise, game):
    def load_reward_profile(agent):
        if args.custom_rewards:
            agent.adjust_rewards(*map(int, args.custom_rewards.split(',')))
        else:
            exercise.reward_profile(agent)
    agent = exercise.get_agent(game)
    if args.custom_actions:
        agent.replace_actions(args.custom_actions)
    agent.reward_scaling([1, -1, -1])
    agent.fov = args.fov
    agent.gamma = args.gamma
    agent.game.suppressed = True
    # train the agent using the provided solution
    load_reward_profile(agent)
    return agent

def evaluate(name, no_initial_training=False):
    # import the solution name into the global namespace as 'exercise'
    exercise = __import__(convert(name))
    name = convert(name)
    # game and agent setup code
    game = Game(do_render=args.render)
    game.set_size(args.grid_size, args.grid_size)
    original_game = copy.copy(game)
    # fetch the agent from the provided solution
    agent = fetch_agent(exercise, game)
    file_name_add = ''
    if not no_initial_training:
        if args.dephase:
            agent.dephase = True
        exercise.train(agent)
    else: 
        file_name_add = 'no_train_'
    # clean up after training
    agent.reward_scaling([1, -1, -1])
    agent.accumulated = 0   # reset accumulated rewards
    agent.set_epsilon(0.0)  # turn off exploration
    agent.game.reset()      # reset the game
    agent.game.high_score = 0
    agent.fov  = args.fov
    agent.game = original_game # if the training modifies the game, it is fixed here
#   load_reward_profile(agent)
    exercise.reward_profile(agent)
    if args.dephase:
        agent.dephase = False
        exercise.train(agent)
    # evaluate the training results
    folder = 'eval_solutions'
    file_name = evaluator.evaluate(agent, name=os.path.join(folder, file_name_add+name))
    # print out a nice summary of how the evaluation went
    summarizer.summarize_e(file_name)
    return file_name

def count_evals(name):
    # import the solution name into the global namespace as 'exercise'
    exercise = __import__(convert(name))
    name = convert('{0}_{1}'.format(args.grid_size, name))
    
    def load_reward_profile(agent):
        if args.custom_rewards:
            agent.adjust_rewards(*map(int, args.custom_rewards.split(',')))
        else:
            exercise.reward_profile(agent)
    # game and agent setup code
    game = Game(do_render=args.render)
    game.set_size(args.grid_size, args.grid_size)
    original_game = copy.copy(game)
    # fetch the agent from the provided solution
    agent = fetch_agent(exercise, game)
    folder = 'reval_solutions'
    configuration = setting_configuration()
    target_path = os.path.join(folder, configuration[0])
    target_filename = os.path.join(target_path, name)
    try:
        os.makedirs(target_path)
    except OSError as e: # silently ignore any errors, other errors _will_ appear if this fails
        import errno
        if e.errno == errno.EEXIST and os.path.isdir(target_path):
            pass
        else: raise
    with open(os.path.join(target_path, 'settings.txt'), 'w') as fh:
        fh.write(configuration[1])
    try:
        os.remove(target_filename + '.txt')
    except OSError:
        pass
    winning = 0
    try:
        for x in xrange(args.max_count):
            game_copy = copy.copy(original_game)
            agent.game = game_copy
            # train the agent using the provided solution
            load_reward_profile(agent)
            agent.learning = True
            print 'training {0}'.format(x)
            if args.custom_training:
                custom_training(agent)
            else:
                exercise.train(agent)
            # clean up after training
            agent.reward_scaling([1, -1, -1])
            agent.accumulated = 0   # reset accumulated rewards
            agent.set_epsilon(0.0)  # turn off exploration
            agent.game.reset()      # reset the game
            agent.game.high_score = 0
            agent.fov  = args.fov
            agent.game = original_game # if the training modifies the game, it is fixed here
            load_reward_profile(agent)
            # evaluate the training results
            print 'evaluation {0}'.format(x)
            file_name = evaluator.random_evaluate(agent, runs=200, name=target_filename)
    #       This is a space hog, I don't have harddrive space to save policies - throstur
    #       agent.learner.dump_policy('count_{0}'.format(x))
            with open(file_name, 'r') as fh:
                lines = fh.read().splitlines()
                if float(lines[-1].split(',')[8]) >= 1:
                    if winning > 10:
                        print 'this one is winning, done'
                        if args.allow_early_finish:
                            break
                    else:
                        winning += 1
                else:
                    winning = max(0, winning - 1)
    except KeyboardInterrupt:
        print 'Quitting early...'
        pass # just stop evaluating
    # print out a nice summary of how the evaluation went
    summarizer.summarize_ec(file_name)
    return file_name


def main():
    if args.dephase:
        file_name = evaluate(args.solution_name)
        file_name2 = evaluate(args.solution_name, no_initial_training=True)
        compare_evals(file_name, file_name2)
    else:
        num_iters = 1 if not args.multi else args.multi
        show = False if args.multi else True
        evals = []
        for iteration_number in range(num_iters):
            if args.outfile and os.path.exists(args.outfile): # what if args.multi?
                raise OSError('The destination file already exists, move it or pick another name.')
            if args.count_evals:
                file_name = count_evals(args.solution_name)
            else:
                file_name = evaluate(args.solution_name)
            if args.outfile or args.multi:
                outname = file_name if not args.outfile else args.outfile
                if args.multi:
                    outname += str(iteration_number)
                os.rename(file_name, outname)
                file_name = outname
            evals.append(file_name)

            if args.count_evals:
                counter_plot(file_name, display=show)
            else:
                evaluation_plot(file_name, display=show)
        if args.multi:
            summarizer.sum_sum(evals)           

def setting_configuration():
    config_lines = []
    for arg in vars(args):
        config_lines.append('{0}: {1}'.format(arg, getattr(args, arg)))
    config_name = '+'.join(sys.argv[1:]).strip('.').strip('/')

    return config_name, '\n'.join(config_lines)+'\n'

def do_initializations():
    sys.path.insert(0, 'solutions') # to avoid needing an __init__.py in the 'solutions' directory
    if not args.seed: # do as random.py source code to generate a random seed
        try:
            from os import urandom as _urandom
            from binascii import hexlify as _hexlify
            a = long(_hexlify(_urandom(16)), 16)
        except NotImplementedError:
            import time
            a = long(time.time() * 256) # use fractional seconds
        args.seed = a
    import random 
    random.seed(args.seed)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RL Learner exercise')
    parser.add_argument('solution_name', default='exercise', nargs='?', help='exercise to evaluate')
    parser.add_argument('--outfile', metavar='FILENAME', help='output file name')
    parser.add_argument('-g', '--grid_size', type=int, default=10, help='grid size')
    parser.add_argument('-f', '--fov', type=int, default=3, help='base field of view')
    parser.add_argument('--gamma', type=float, default=0.8, metavar='FLOAT', help='discount factor')
    parser.add_argument('-c', '--compare_to', metavar='OTHER_FILE', help='compare two solutions')
    parser.add_argument('--custom_rewards', metavar='CHEESE,TRAP,HUNGER', help='reward profile in the format "c,t,h" (without quotes)')
    parser.add_argument('--dephase', action='store_true', help=u'swap reward scalars (180\N{DEGREE SIGN} out of phase)')
    parser.add_argument('--count_evals', action='store_true', help='run random evaluations')
    parser.add_argument('--max_count', type=int, metavar='MAX', default=100, help='maximum number of steps to count to during count evaluations')
    parser.add_argument('--allow_early_finish', action="store_true", help='allow the count to end early if the solution is good')
    parser.add_argument('--custom_training', type=int, metavar='STEPS', help='custom number of training steps per session (training only `performs` on the agent)')
    parser.add_argument('--custom_actions', type=lambda s: [item.strip() for item in s.split(',')], metavar='"left,right,forward,?",...', help='Replace solution actions with custom actions')
    parser.add_argument('--multi', type=int, metavar='N', help='number of evaluations to make (single evaluations only)')
    parser.add_argument('--seed', type=int, metavar='N', default=0, help='random seed (0 means system time)')
    parser.add_argument('--render', action='store_true', help='render the evaluation (not recommended, greatly affects performance)')
    args = parser.parse_args()
    do_initializations()
    try:
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
        


