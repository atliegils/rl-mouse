#!/usr/bin/python2
import argparse
import math, os, sys, traceback
import agent, threading, time
import pickle
from learners import QLearn, SARSA
from game import Game
from pprint import pprint

def save_policy(learner, name):
    policy = learner.q
    with open(name + '.policy', 'wb') as f:
        pickle.dump(policy, f)

def load_policy(learner, name):
    with open(name + '.policy', 'rb') as f:
        policy = pickle.loads(f.read())
        learner.q = policy

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
    learner.exploration_rate = 0.10 # encourage exploration
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
#       action1 = learner.select(state1)
        player.game.play(action1)
        reward = player.check_reward()
        state2 = player.get_fov(args.fov)
        administer_reward(learner, reward, state1, action1, state2)
        seconds_passed = time.time() - t_start
    player.reset_game()

def dist_to_cheese(game):
    assert game.width == game.height, 'not a square grid'
    gz = game.width
    max_len = (gz + 1) / 2 # looped grid
    mouse = game.mouse
    cheese = game.cheese
    dx = mouse[0] - cheese[0]
    dy = mouse[1] - cheese[1]
    direct = abs(dx) + abs(dy)
    # mouse could go through walls, consider extra options
    distances = [direct] 
    xs = []
    ys = []
    def align(x):
        return (x + gz) % gz
    for i in xrange(gz):
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
    if dx == 0 or dy == 0 and gz > 3:
        if game.direction == 'up' and mouse[1] + 1 == cheese[1]:
            add = 2
        elif game.direction == 'down' and mouse[1] - 1 == cheese[1]:
            add = 2
        elif game.direction == 'left' and mouse[0] + 1 == cheese[0]:
            add = 2
        elif game.direction == 'right' and mouse[0] - 1 == cheese[0]:
            add = 2

    return min(dist + add, max_len)

def benchmark(player, max_runs=5000):
    player.game.suppressed = True
    outfile = 'test.txt'
    if args.outfile:
        outfile = args.outfile
    # no overwrite warning here

    i = 0
    start_step = 0
    deaths = 0
    dist = dist_to_cheese(player.game)
    data = []
    last = [0]
    local_length = 10 * args.round_limit
    accum = [0] * local_length
    while len(data) < max_runs:
        i = i + 1
        if len(data) % (max_runs/10) == 0:
            pass # here I would save the policy           
        if i - start_step > args.round_limit: # our agent is probably in a loop
            if args.verbose:
                print 'timeout in game {0} at step {1}'.format(len(data) + 1, i)
            average = sum(last) / float(len(last))
            local_reward = sum(accum[-local_length:])
            dp = (0, -1, average, player.accumulated, local_reward)
            data.append(dp)
            start_step = i
            deaths = 0
            player.reset_game()
            dist = dist_to_cheese(player.game)
        else:
            eee = False
            if args.test:
                eee = True
            if args.meta:
                reward = player.perform(last_action=True, verbose=args.verbose)
            else:
                reward = player.perform(explore=eee, last_action=True, verbose=args.verbose)
            accum.append(reward)
        if reward == 1:
            if data:
                last = [x[0] for x in data[-100:]]
            average = sum(last) / float(len(last))
            score = dist / float(i - start_step)
            local_reward = sum(accum[-local_length:])
            dp = (score, deaths, average, player.accumulated, local_reward)
            data.append(dp)
            start_step = i
            deaths = 0
            player.reset_game()
            dist = dist_to_cheese(player.game)
            # verbose
            if args.verbose == 2:
                print average, deaths, score
            if args.verbose == 1 or args.verbose > 3:
                print '{0}/{1}'.format(len(data), max_runs)
            # end verbose
        if reward == -1:
            deaths += 1
            dist = dist_to_cheese(player.game) # the player was respawned
    with open(outfile, 'w') as f:
        for dp in data:
            f.write(','.join(map(str,list(dp))) + '\n')

def configure_game(player, d_cheese, d_trap, start_dir):
    assert d_cheese != d_trap, 'cheese and trap in same location'
    c_dx, c_dy = d_cheese
    t_dx, t_dy = d_trap
    player.game.direction = start_dir
    player.game.mouse = 3, 3
    player.game.cheese = player.offset(c_dx, c_dy)
    player.game.trap = player.offset(t_dx, t_dy)
    
def generate_configurations():
    col = []
    dirs = ['up', 'right']#, 'down', 'left']
    for dd in dirs:
        for offset in xrange(-3, 4, 1):
            for off2 in xrange(-2, 3, 1):
                for c in xrange(5):
                    for t in xrange(5):
                        if t == c: continue
                        dc = c, c + offset 
                        dt = t, t + off2
                        config = dc, dt, dd
                        col.append(config)
    return col

def pong_evaluate(player, runs=200, name='pong_eval', max_count=3000):
    player.game.suppressed = True
    player.learning = False
    outfile = name + '.txt'
    wins = 0
    loss = 0
    data = []
    for _ in xrange(runs):
        winner = 0
        count = 0
        while not winner and count <= max_count:
            count = count + 1
            winner = player.perform()
            if winner == 1:
                wins += 1
            elif winner == 2:
                loss += 1   
            if winner or count == max_count:
                data.append(winner)
#               if winner: print winner
                if not winner: print 'count'
        player.game.reset(soft=True)
    dirname = os.path.dirname(outfile)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(outfile, 'a') as f:
#       print 'W {0} | {1} L'.format(wins, loss)
#       f.write(','.join(map(str, list(data))) + '\n')
        f.write('{0},{1}'.format(wins, loss) + '\n')
    return outfile, wins, loss

def random_evaluate(player, runs=200, round_limit=300, name='rand_eval'):
    target_limit = player.game.width * player.game.height / 2
    if target_limit > round_limit:
        round_limit = target_limit
        print 'setting round limit to {0}'.format(round_limit)
    player.game.suppressed = True
    player.learning = False
    outfile = name + '.txt'
    timeouts     = 0
    deaths       = 0
    extra_steps  = 0 # NOTE: Special snowflake, see how used in evaluate
    target_steps = 0 
    data         = []
    accumulated_reward = [] 
    for _ in xrange(runs):
        current_step = 0
        local_deaths = 0
        player.reset_game()
        target_distance = dist_to_cheese(player.game)
        while current_step < round_limit:
            current_step += 1
            player.game.render()
            reward = player.perform()
            accumulated_reward.append(reward)
            if reward == -1:
                deaths += 1
                local_deaths += 1
            if reward == 1: # cheese was acquired
                break
        else:   # no cheese was acquired before timeout
            print 'timeout'
            timeouts += 1
        extra_steps += current_step - target_distance
        target_steps += target_distance
    # create data point
    ratio = float(target_steps) / (extra_steps + target_steps)
    data_point = (player.game.score, deaths, timeouts, player.accumulated, 0, local_deaths, extra_steps, ratio, 0)
    # save data point
    data.append(data_point)
    dirname = os.path.dirname(outfile)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(outfile, 'a') as f:
        for datum in data:
            print 'writing:',','.join(map(str, list(datum))) + '\n'
            f.write(','.join(map(str, list(datum))) + '\n')
    return outfile

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
    # configure game object
    game = Game()
    g = args.grid_size
    game.set_size(g, g)
    if args.difficulty == 2:
        game.cat = True
    elif args.difficulty == 0:
        game.easy = True
    # configure player object
    if args.meta:
        if args.test:
            player = agent.CheeseMeta(game, ['left', 'forward', 'right'], exploration_rate=args.exploration_rate, fov=args.fov)
        else:
            player = agent.MetaAgent(game, ['left', 'forward', 'right'], exploration_rate=args.exploration_rate, fov=args.fov)
        player.side = args.side
    else:
        player = agent.Agent(game, ['left', 'forward', 'right'])
    player.adjust_rewards(abs(args.cheese_reward), abs(args.trap_reward), abs(args.hunger_reward))
    
    # boilerplate for CLI
    t = threading.Thread(target=command, args=(player,))
    t.daemon = True
    t.start()
    # launch point
    if args.meta or args.benchmark:
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
    parser.add_argument('-cr', '--cheese_reward', type=int, default=5, help='reward for eating cheese')
    parser.add_argument('-tr', '--trap_reward', type=int, default=-10, help='reward for getting caught in a trap (should be negative)')
    parser.add_argument('-hr', '--hunger_reward', type=int, default=-1, help='reward for not eating cheese or doing anything important')
    parser.add_argument('-g', '--grid_size', type=int, default=7, help='grid size')
    parser.add_argument('-e', '--exploration_rate', type=float, default=0.02, help='custom exploration_rate value')
    parser.add_argument('--data_interval', type=int, metavar='N', default=1, help='only write every Nth datapoint')
    parser.add_argument('--round_limit', type=int, metavar='N', default=0, help='limit rounds to N steps')
    parser.add_argument('--fov', type=int, default=3, help='how far the agent can see')
    parser.add_argument('-v', '--verbose', action='count', help='increase output verbosity')
    parser.add_argument('-b', '--benchmark', action='store_true', help='normalize data by counting steps')
    parser.add_argument('-hd', '--history_depth', type=int, default=3, help='history depth')
    parser.add_argument('-s', '--side', default='', help='side for meta learner')
    parser.add_argument('--meta', action='store_true', help='test history agent')
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
