#!/usr/bin/python2
import argparse
import math, os, sys, traceback
import agent, threading, time
from learners import QLearn, SARSA
from game import Game
from pprint import pprint

def administer_reward(learner, reward, next_state=None):
    if reward == 1:
        value = args.cheese_reward
    elif reward == -1:
        value = args.trap_reward
    else:
        value = args.hunger_reward
    if not next_state: # SARSA Learner
        learner.learn(value)
    else:              # Q-Learner
        learner.learn(value, next_state)

def warn_overwrite(outfile):
    if os.path.exists(outfile):
        c = raw_input('WARNING: output file {0} already exists, continue?\n'.format(outfile)).lower()
        if not c.startswith('y'):
            sys.exit(0)

def create_datapoint(score, high_score, last_scores, diff_local=False):
    high_score = max(score, high_score)
    last_scores.append(score)
    if diff_local:
            local_high = max(last_scores[-max(args.data_interval, max_runs/10):])
    else:
        local_high = max(last_scores[-100:])
    datapoint = ','.join(map(str, [score, high_score, local_high]))
    return datapoint

def train(player, learner, max_runs=10000):
    actions = ['left', 'forward', 'right']
    i = 0
    learner.epsilon = 0.10 # encourage exploration
    t_start = time.time()
    time_limit = 1.0
    seconds_passed = 0.0
    player.game.set_size(3, 3)
    s = 3
    while i < max_runs:
        if i % (max_runs / 4) == 0:
            s = s + 1
            player.game.set_size(s, s)
        if seconds_passed >= time_limit:
            player.reset_game()
            t_start = time.time()
        i = i + 1
        state1 = player.get_fov(args.fov)
        action1 = learner.select(state1)
        player.game.play(action1)
        reward = player.check_reward()
        state2 = player.get_fov(args.fov)
        administer_reward(learner, reward, state1, action1, state2)
        seconds_passed = time.time() - t_start
    player.reset_game()

def dist_to_cheese(game):
    mouse = game.mouse
    cheese = game.cheese
    dx = mouse[0] - cheese[0]
    dy = mouse[1] - cheese[1]
    direct = abs(dx) + abs(dy)
    # mouse could go through walls, consider extra options
    distances = [direct] 
    shift = args.grid_size / 2
    def align(x):
        return (x + args.grid_size) % args.grid_size
    xs = []
    ys = []
    for i in xrange(args.grid_size):
        dx = align(i + mouse[0]) - align(i + cheese[0])
        dy = align(i + mouse[1]) - align(i + cheese[1])
        xs.append(abs(dx))
        ys.append(abs(dy))
#   result = min(xs) + min(ys)
#   dist = 2 * args.grid_size - max(mouse[0], cheese[0]) + min(mouse[0], cheese[0]) - max(mouse[1], cheese[1]) + min(mouse[1], cheese[1])
    ddx = min(xs)
    ddy = min(ys)
    dist = ddx + ddy;
    add = 0
    # add 2 to the distance IFF direction is opposite
#   if ddx == 0 or ddy == 0:
    if dx == 0 or dy == 0 and args.grid_size > 3:
        if game.direction == 'up' and mouse[1] + 1 == cheese[1]:
            add = 2
        elif game.direction == 'down' and mouse[1] - 1 == cheese[1]:
            add = 2
        elif game.direction == 'left' and mouse[0] + 1 == cheese[0]:
            add = 2
        elif game.direction == 'right' and mouse[0] - 1 == cheese[0]:
            add = 2

    return dist + add

def benchmark(player, max_runs=5000):
    actions = ['left', 'forward', 'right']
    player.game.suppressed = True
    outfile = 'standard.txt'
    if args.outfile:
        outfile = args.outfile
    warn_overwrite(outfile)
    # init learners
    learner = SARSA(actions, args.epsilon)
    g = args.grid_size
    player.game.set_size(g, g)
    # simulate
    i = 0
    start_step = 0
    deaths = 0
    dist = dist_to_cheese(player.game)
    data = []
    last = [0]
    while len(data) < max_runs:
        i = i + 1
        state1 = player.get_fov(args.fov)
        learner.set_state(state1)
        action1 = learner.select()
        if args.verbose == 3:
            from pprint import pprint
            player.game.render()
            pprint(learner.q)
            print state1
            print 'min dist: {0}, choice: {1}\n'.format(dist, action1)
            c = raw_input()
            if c:
                action1 = c
                learner.current_action = action1
            if 'q' in c:
                args.verbose = 1
            player.game.render()
        player.game.play(action1)
        reward = player.check_reward()
        administer_reward(learner, reward)
        if reward == 1: # count steps between cheeses
            if data:
                last = [x[0] for x in data[-100:]]
            average = sum(last) / float(len(last))
            score = dist / float(i - start_step)
            dp = (score, deaths, average)
            data.append(dp)
            if args.verbose >= 2:
                print dp
            if args.verbose == 1 or args.verbose > 3:
                print '{0}/{1}'.format(len(data), max_runs)
            start_step = i
            deaths = 0
            player.reset_game()
            dist = dist_to_cheese(player.game)
        if reward == -1:
            deaths += 1
            dist = dist_to_cheese(player.game) # the player was respawned
    with open(outfile, 'w') as f:
        for dp in data:
            f.write(','.join(map(str,list(dp))) + '\n')

def evaluate(player, max_runs=5000):
    actions = ['left', 'forward', 'right']
    # game set up
    player.game.suppressed = True
    outfile = 'default.txt'
    if args.outfile:
        outfile = args.outfile
    warn_overwrite(outfile)
    with open(outfile, 'w') as f:
        # initialize the learners
        learner = SARSA(actions, args.epsilon)
        train(player, learner, args.training_steps)
        # don't render evaluations (unless the user asks)
        player.game.suppressed = True
        learner.epsilon = args.epsilon  # other game 
        g = args.grid_size              # setup based
        player.game.set_size(g, g)      # on params
        if args.verbose:
            print 'training complete'
        # round control
        t_start = time.time()
        time_limit = 5.0
        start_step = 0
        seconds_passed = 0.0
        # bookkeeping ####
        high_score = 0   #
        last_scores = [] #
        data = []        #
        # end bookkeeping#
        i = 0
        step = 0
        # main evaluation loop
        while i < max_runs:
            # record the time for a timeout
            seconds_passed = time.time() - t_start
            if seconds_passed > time_limit or step - start_step > args.round_limit and args.round_limit > 0:
                player.reset_game()
                t_start = time.time()   # reset round time
                start_step = step       # reset round steps
                if args.game_limit:     # write data since this is 'like death'
                    i = i + 1
                    high_score = max(score, high_score)
                    datapoint = create_datapoint(score, high_score, last_scores)
                    data.append(datapoint)
                    if i % 100 == 0:
                        for datum in data:
                            f.write(str(datum) + '\n')
                        if args.verbose:
                            print 'average: {0}, timeout {1}, high {2}, {3}'.format(sum([int(x.split(',')[0]) for x in data]) / len(data), i, high_score, str(max(last_scores[-100:])))
                        data = []
                        last_scores = last_scores[-100:]
            step = step + 1
            # get an appropriate field of view based on grid size
            state1 = player.get_fov(args.fov)
            action1 = learner.select(state1)
            player.game.play(action1)
            reward = player.check_reward()
            state2 = player.get_fov(args.fov)
            administer_reward(learner, reward, state1, action1, state2)
#           state = player.get_fov(max(3,3+g/2))
#           learner.set_state(state)    # set leraner state
#           selection = learner.select()# select an action
#           player.game.play(selection) # play selected action
#           # check if the action we chose was any good
#           reward = player.check_reward()
            score = player.game.score   # record score in case it gets changed now
#           # reward control flow etc
#           administer_reward(learner, reward)
            if reward == 1:     # cheese
                t_start = time.time() # reset the timeout, not in loop yet
            elif reward == -1:  # trap
                player.game.score = 0 # reset the score
                # datapoint = right before death
                if args.game_limit:   
                    datapoint = create_datapoint(score, high_score, last_scores)
                    data.append(datapoint)
                    i = i + 1
                    if i % 100 == 0:
                        for datum in data:
                            f.write(str(datum) + '\n')
                        if args.verbose:
                            print 'average: {0}, iteration {1}, high {2}, {3}'.format(sum([int(x.split(',')[0]) for x in data]) / len(data), i, high_score, str(max(last_scores[-100:])))
                        data = []
            # reward has been administered and data has been written IF we're writing on deaths
            if args.verbose > 3:
                print 'received reward {0} for action {1} in state {2}'.format(reward, action1, state1)
            high_score = max(score, high_score)
            if not args.game_limit: # datapoint = every action
                i = i + 1
                score = player.game.score
                if i % args.data_interval == 0:
                    datapoint = create_datapoint(score, high_score, last_scores, diff_local=True)
                    data.append(datapoint)
                if data and i % 100 == 0:
                    for datum in data:
                        f.write(str(datum) + '\n')
                    if args.verbose:
                        print 'average: {0}, action {1}, high {2}, {3}'.format(sum([int(x.split(',')[0]) for x in data]) / len(data), i, high_score, local_high)
                    data = []
            # data has been written if data_interval is 1 or if the modulo is zero
            if args.verbose >= 3:
                print '                                                             {0}\r'.format(i),
            if args.verbose == 9: # verbose 9 is for debugging
                raw_input('continue?')
        # end of evaluations
        for datum in data: # write any remaining data
            f.write(str(datum) + '\n')
        print 'all done'
        sys.exit(0)


# interactive command line
def command(player):
    time.sleep(2) # give the main thread some time to prompt the user etc before taking over
    while True:
        if args.verbose == 3:
            time.sleep(1)
            continue
        try:
            text = raw_input('> ')
            if 'render' in text or 'sup' in text or 'draw' in text: # toggle rendering
                player.game.suppressed = not player.game.suppressed
                print 'rendering ->', not player.game.suppressed
            if text.strip().isdigit():  # set verbose level (e.g. 1 -> args.verbose := 1)
                args.verbose = int(text.strip())
            if 'q' in text:             # stop the simulation
                player.game.force_kill = True
                sys.exit(9)
        except EOFError:                # CTRL+D also stops the simulation
            player.game.force_kill = True
            sys.exit(9)

def main():
    global args
    game = Game()
    if args.difficulty == 2:
        game.cat = True
    elif args.difficulty == 0:
        game.easy = True
    player = agent.Agent(game)
    t = threading.Thread(target=command, args=(player,))
    t.daemon = True
    t.start()
    if args.benchmark:
        benchmark(player, max_runs=args.max_actions)
    else:
        evaluate(player, max_runs=args.max_actions)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mouse q-learner evaluator')
    parser.add_argument('-o', '--outfile', help='where to store the results')
    parser.add_argument('-m', '--max_actions', type=int, default=15000, help='maximum number of moves the agent can make')
    parser.add_argument('-l', '--game_limit', action='store_true', help='max actions refers to games, not actions')
    parser.add_argument('-t', '--training_steps', type=int, default=10000, help='number of training steps')
    parser.add_argument('-d', '--difficulty', type=int, choices=[0, 1, 2], help='0: easy, 1: trap, 2: cat')
    parser.add_argument('-cr', '--cheese_reward', type=int, default=100, help='reward for eating cheese')
    parser.add_argument('-tr', '--trap_reward', type=int, default=-1000, help='reward for getting caught in a trap (should be negative)')
    parser.add_argument('-hr', '--hunger_reward', type=int, default=-1, help='reward for not eating cheese or doing anything important')
    parser.add_argument('-g', '--grid_size', type=int, default=7, help='grid size')
    parser.add_argument('-e', '--epsilon', type=float, default=0.05, help='custom epsilon value')
    parser.add_argument('--data_interval', type=int, metavar='N', default=1, help='only write every Nth datapoint')
    parser.add_argument('--round_limit', type=int, metavar='N', default=0, help='limit rounds to N steps')
    parser.add_argument('--fov', type=int, default=3, help='how far the agent can see')
    parser.add_argument('-v', '--verbose', action='count', help='increase output verbosity')
    parser.add_argument('-b', '--benchmark', action='store_true', help='normalize data by counting steps')
    parser.add_argument('--test', action='store_true', help='debug')
    args = parser.parse_args()
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except SystemExit:
        sys.exit(0)
    except Exception, e:
        print traceback.print_exc()
        print e
        sys.exit(1)
