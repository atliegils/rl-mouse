#!/usr/bin/python2
import evaluator
from plotter import pong_plot
from pong import Pong
import argparse, copy
import os, sys, traceback

def convert(name):
    return name.rstrip('.py').replace('/','.').replace('solutions.','')

def setting_configuration():
    config_lines = []
    for arg in vars(args):
        config_lines.append('{0}: {1}'.format(arg, getattr(args, arg)))
    config_name = '+'.join(sys.argv[1:]).strip('.').strip('/')
    return config_name, '\n'.join(config_lines)+'\n'

def pong_eval(name):
    # import the solution name into the global namespace as 'exercise'
    exercise = __import__(convert(name))
    name = convert('{0}'.format(name))
    # game and agent setup code
    game = Pong(do_render=args.render)
#   game.render_time = 0.00001 # immediate rendering (visual debugging)
    original_game = copy.copy(game)
    # fetch the agent from the provided solution
    agent = exercise.get_agent(game)
    folder = 'pong_evaluation'
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
    for x in xrange(args.initial_training - 1):
        game_copy = copy.copy(original_game)
        game_copy.do_render = False     # don't render initial training
        agent.game = game_copy
        agent.learning = True
        exercise.train(agent)
    winning = 0
    try:
        for x in xrange(args.training_epochs):
            game_copy = copy.copy(original_game)
            game_copy.do_render = False     # don't render training
            agent.game = game_copy
            # train the agent using the provided solution
            agent.learning = True
            exercise.train(agent)
    #       agent.learner.dump_policy(str(x))
            # clean up after training
            agent.accumulated = 0   # reset accumulated rewards
            agent.set_exploration_rate(0.0)  # turn off exploration
            agent.game.reset()      # reset the game
            agent.game = original_game # if the training modifies the game, it is fixed here
            # evaluate the training results
            agent.game.do_render = args.render
            print 'evaluating'
            file_name, wins, loss = evaluator.pong_evaluate(agent, runs=args.eval_games, name=target_filename, max_count=1000)
            if wins > loss * 10:
                winning += 1
                if winning > 10:
                    print 'solution succeeds'
            else:
                winning = max(0, winning - 1)
            print 'W {0} | {1} L | Round: {2}'.format(wins, loss, x)
    except KeyboardInterrupt:
        print '\rEARLY INTERRUPT!'
    return file_name
    

def main():
    fn = pong_eval(args.solution_name)
    pong_plot(fn, True)

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
    parser = argparse.ArgumentParser(description='Pong RL Agent evaluator')
    parser.add_argument('solution_name', default='solutions/pong_sarsa', nargs='?', help='solution to evaluate')
    parser.add_argument('--eval_games', type=int, metavar='NUM', default=200, help='Number of games to play per evaluation')
    parser.add_argument('--initial_training', type=int, metavar='EPOCHS', default=1, help='number of training epochs to give the agent before the first evaluation')
    parser.add_argument('--training_epochs', type=int, metavar='MAX', default=100, help='maximum number of training epochs')
    parser.add_argument('--seed', type=int, metavar='N', default=0, help='random seed (0 means system time)')
    parser.add_argument('--render', action='store_true', help='render pong')
    args = parser.parse_args()
    do_initializations()
    try:
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
        
