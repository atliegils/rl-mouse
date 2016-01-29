#!/usr/bin/python2
import argparse
import copy
import evaluator
import summarizer
import os, sys, traceback
from environment import MouseEnvironment, RidgeEnvironment

def load_reward_profile(agent):
    if args.custom_rewards:
        agent.adjust_rewards(*map(int, args.custom_rewards.split(',')))
    else:
        agent.adjust_rewards(2,3,1)

def comparison():
    folder = 'comparisons'
    configuration = setting_configuration()
    target_path = os.path.join(folder, configuration[0])
    try:
        os.makedirs(target_path)
    except OSError as e: # silently ignore any errors, other errors _will_ appear if this fails
        import errno
        if e.errno == errno.EEXIST and os.path.isdir(target_path):
            pass
        else: raise
    with open(os.path.join(target_path, 'settings.txt'), 'w') as fh:
        fh.write(configuration[1])

    e1 = count_epochs(args.solution_name)
    e2 = count_epochs(args.compare_to)
    compare_evals(e1, e2) 

def convert(name):
    return name.rstrip('.py').replace(os.sep,'.').replace('solutions.','')

def custom_training(agent):
    # agent.set_exploration_rate(0.1) # just rely on the command line or default settings of the agent
    for i in xrange(args.custom_training):
        agent.perform()

def fetch_agent(exercise, game):
    agent = exercise.get_agent(game)
    if args.custom_actions:
        agent.replace_actions(args.custom_actions)
    agent.reward_scaling([1, -1, -1])
    # agent.fov = args.fov
    if 0 <= args.discount_factor <= 1:
        agent.learner.discount_factor = args.discount_factor
    if 0 <= args.exploration_rate <= 1:
        agent.set_exploration_rate(args.exploration_rate)
    if 0 <= args.learning_rate <= 1:
        agent.learner.learning_rate = args.learning_rate
    if hasattr(agent, 'fov') and (args.fov > 0 or not agent.fov):
        print 'fov', agent.fov
        agent.fov = args.fov if args.fov > 0 else 3
        print 'fov', agent.fov
        raw_input('')
    agent.game.suppressed = True
    # train the agent using the provided solution
    load_reward_profile(agent)
    return agent

def count_epochs(name):
    # import the solution name into the global namespace as 'exercise'
    exercise = __import__(convert(name))
    name = convert('{0}_{1}'.format(args.grid_size, name))
    no_runs = 200
    
    # game and agent setup code
    if args.environment == 'ridge':
        game = RidgeEnvironment(do_render=args.render)
        game.set_size(args.grid_size, 3)
        dist_func = evaluator.dist_to_ridge_goal
        no_runs = 100
    else:
        game = MouseEnvironment(do_render=args.render)
        game.set_size(args.grid_size, args.grid_size)
        dist_func = evaluator.dist_to_cheese
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
        for x in xrange(args.max_epochs):
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
            # agent.set_exploration_rate(0.0)  # turn off exploration # or don't: let the user do it if they want
            agent.game.reset()      # reset the game
            agent.game.high_score = 0
            # agent.fov  = args.fov
            agent.game = original_game # if the training modifies the game, it is fixed here
            load_reward_profile(agent)
            # evaluate the training results
            print 'evaluation {0}'.format(x)
            file_name = evaluator.random_evaluate(agent, runs=no_runs, name=target_filename, distance=dist_func)
    #       This is a space hog, I don't have harddrive space to save policies - throstur
    #       agent.learner.dump_policy('count_{0}'.format(x))
            with open(file_name, 'r') as fh:
                lines = fh.read().splitlines()
    except KeyboardInterrupt:
        print 'Quitting early...'
        pass # just stop evaluating
    # print out a nice summary of how the evaluation went
    agent.learner.dump_policy(name)
    summarizer.summarize(file_name)
    return file_name

# TODO: needs work
def dephase():
    file_name = count_evals(args.solution_name)
    file_name2 = count_evals(args.solution_name, initial_training=False)
    compare_evals(file_name, file_name2)

def main():
    num_iters = args.multi or 1
    show = not args.multi
    evals = []
    for iteration_number in range(num_iters):
        if args.outfile and os.path.exists(args.outfile): # what if args.multi?
            raise OSError('The destination file already exists, move it or pick another name.')
        file_name = count_epochs(args.solution_name)
        if args.outfile or args.multi:
            outname = args.outfile or file_name
            if args.multi:
                outname += str(iteration_number)
            os.rename(file_name, outname)
            file_name = outname
        evals.append(file_name)
        counter_plot(file_name, display=show)
    if args.multi:
        summarizer.summarize_multiple_evaluations(evals)

def setting_configuration():
    def filter_cname(text):
        import re
        matches = re.findall(r'--[a-zA-Z\_]*', text)
        for match in matches:
            target = match
            replacement = match[2:5]
            text = text.replace(target, replacement)
        return text
    config_lines = []
    for arg in vars(args):
        config_lines.append('{0}: {1}'.format(arg, getattr(args, arg)))
    config_name = '+'.join(sys.argv[1:]).strip('.').strip(os.sep)
    config_name = filter_cname(config_name)

    return config_name, '\n'.join(config_lines)+'\n'

def do_initializations():
    # adds solutions dir to the path and seeds the random number generator

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
    parser.add_argument('-f', '--fov', type=int, default=0, help='base field of view')
    parser.add_argument('--discount_factor', type=float, default=-1, metavar='FLOAT', help='discount factor [0,1]')
    parser.add_argument('--learning_rate', type=float, default=-1, metavar='FLOAT', help='learning rate [0,1]')
    parser.add_argument('--exploration_rate', type=float, default=-1, metavar='FLOAT', help='exploration rate [0,1]')
    parser.add_argument('-c', '--compare_to', metavar='OTHER_FILE', help='compare two solutions')
    parser.add_argument('--custom_rewards', metavar='CHEESE,TRAP,HUNGER', help='reward profile in the format "c,t,h" (without quotes)')
    parser.add_argument('--dephase', action='store_true', help=u'swap reward scalars (180\N{DEGREE SIGN} out of phase)')
    parser.add_argument('--max_epochs', type=int, metavar='MAX', default=100, help='maximum number of epochs to count to during count evaluations')
    parser.add_argument('--custom_training', type=int, metavar='STEPS', help='custom number of training steps per session (training only `performs` on the agent)')
    parser.add_argument('--custom_actions', type=lambda s: [item.strip() for item in s.split(',')], metavar='"left,right,forward,?",...', help='Replace solution actions with custom actions')
    parser.add_argument('--multi', type=int, metavar='N', help='number of evaluations to make (single evaluations only)')
    parser.add_argument('--seed', type=int, metavar='N', default=0, help='random seed (0 means system time)')
    parser.add_argument('--render', action='store_true', help='render the evaluation (not recommended, greatly affects performance)')
    parser.add_argument('--no_plot', action='store_true', help='disable plotting')
    parser.add_argument('--environment', default='mouse', help='the name of the environment (mouse or ridge)')

    args = parser.parse_args()
    do_initializations()
    try:
        if not args.no_plot:
            from plotter import compare_evals, counter_plot
        if args.compare_to:
            comparison()
        elif args.dephase:
            dephase()
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
        


