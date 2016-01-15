#!/usr/bin/python2
import os
import pickle

def save_qtable(learner, name):
    qtable = learner.q
    with open(name + '.qtable', 'wb') as f:
        pickle.dump(qtable, f)

def load_qtable(learner, name):
    with open(name + '.qtable', 'rb') as f:
        qtable = pickle.loads(f.read())
        learner.q = qtable

def dist_to_cheese(game):
    assert game.width == game.height, 'not a square grid'
    cheese_x, cheese_y = game.get_relative_location(game.cheese)
    trap_x, trap_y = game.get_relative_location(game.trap)
    size = game.width

    if cheese_x == 0 and cheese_y == 0:
        return 0
    elif abs(trap_x) > 1 and trap_y != 0: # easy check to see the trap is definitely not in the way
        dx = abs(cheese_x)
        dy = abs(cheese_y)
        if dx == 0 and cheese_y < 0:
            # if the cheese is straight behind the mouse, is it faster to turn
            # around or walk straight around the (circular) grid?
            dy = min(2 - cheese_y, size + cheese_y)
        return dx + dy
    elif cheese_x == 0: # cheese in current lane
        # how far is it if we turn around? we can do left or right, so a single trap won't be a problem
        turn_dist = 2 + (-cheese_y if cheese_y < 0 else (size + cheese_y))
        if turn_dist < cheese_y:
            return turn_dist

        if cheese_y > 0:
            straight_dist = cheese_y
            if trap_x == 0 and 0 < trap_y < cheese_y:
                straight_dist += 2
        else:
            straight_dist = size + cheese_y
            if trap_x == 0 and (0 < trap_y <= size / 2 or trap_y < cheese_y):
                straight_dist += 2
        return min(straight_dist, turn_dist)
    elif cheese_y > 0 or cheese_x == size / 2 and size % 2 == 0:
        # moving up and to side (or side and up)
        # or moving left and right is same distance
        return abs(cheese_y) + abs(cheese_x)
    elif cheese_y == 0: # cheese to left or right or one row behind
        dist = abs(cheese_x)
        if (trap_y == 0 # trap on same horizontal lane
            and abs(trap_x) < abs(cheese_x) # trap is closer
            and trap_x * cheese_x > 0): # trap is on the same side

            if size % 2 == 1 and abs(cheese_x) == size / 2:
                dist += 1 # walk around. if width is even this takes 0 steps (already handled above) or 2
            else:
                dist += 2
        return dist
    else: # at this point we know that the cheese is behind the mouse
        dist = abs(cheese_x) + abs(cheese_y)
        if (trap_x * cheese_x > 0         # cheese and trap on the same side
            and abs(trap_x) == 1          # trap is one step to left/right
            and (trap_y == 0              # and next to the mouse
                 or trap_y < 0            # or the trap is also behind
                 and abs(cheese_x) == 1   # and the mouse is in the same lane
                 and trap_y > cheese_y)): # and the trap is closer than the cheese

            if size % 2 == 1 and (abs(cheese_x) == size / 2 or abs(cheese_y) == size / 2):
                dist += 1 # walk around. if width is even this takes 0 steps (already handled above) or 2
            else:
                dist += 2
        return dist

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
    data_point = (deaths, timeouts, ratio, player.accumulated, extra_steps)
#   data_point = (player.game.score, deaths, timeouts, player.accumulated, 0, local_deaths, extra_steps, ratio, 0)
    # save data point
    data.append(data_point)
    dirname = os.path.dirname(outfile)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(outfile, 'a') as f:
        for datum in data:
            print 'writing:',',\t'.join(map(str, list(datum))) + '\n'
            f.write(','.join(map(str, list(datum))) + '\n')
    return outfile
