import argparse
def avg(arr):
    return sum(arr)/len(arr)

def sum_sum(names):
    assert(names)
    all_performances  = []
    worst_performance = 1.0
    best_performance  = 0.0
    total_extra       = 0.0
    least_extra       = float('inf')
    most_extra        = 0.0
    least_timeouts    = float('inf')
    most_timeouts     = 0.0
    least_deaths      = float('inf')
    most_deaths       = 0.0
    magics = []
    for name in names:
        _, _, _, d, t, es, ar, _, m = summarize_e(name)
        # performance
        worst_performance = min(ar, worst_performance)
        best_performance = max(ar, best_performance)
        all_performances.append(ar)
        # extra steps
        least_extra = min(es, least_extra)
        most_extra = max(es, most_extra)
        # timeouts
        least_timeouts = min(t, least_timeouts)
        most_timeouts = max(t, most_timeouts)
        # deaths
        least_deaths = min(d, least_deaths)
        most_deaths = max(d, most_deaths)
        magics.append(m)
    average_performance = sum(all_performances)/len(all_performances)
    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    print 'Summary report for {0} evaluations:'.format(len(names))
    print 'Performance: MIN {0} || MAX {1} || AVG {2}'.format(worst_performance, best_performance, average_performance)
    print 'Extra steps: MIN {0} || MAX {1}'.format(least_extra, most_extra)
    print 'Timeouts   : MIN {0} || MAX {1}'.format(least_timeouts, most_timeouts)
    print 'Deaths     : MIN {0} || MAX {1}'.format(least_deaths, most_deaths)
    print 'Eval score : MIN {0} || MAX {1} || AVG {2}'.format(min(magics), max(magics), sum(magics)/len(magics))
    print '_____________________________________________________'

def summarize_e(name):
    print '========================'
    print '{0} summary:'.format(name)

    high_score = 0
    deaths = 0
    timeouts = 0
    best_local = 0
    bl_round = -1
    extra_steps = 0
    ratios = []
    with open(name, 'r') as f:
        text = f.read()
        for cur_step, line in enumerate(text.splitlines()):
            parts = map(float, line.split(',')) # round eff, deaths, average, cumul, local
            score = parts[0]
            deaths = parts[1]
            timeouts = parts[2]
            accumulated_reward = parts[3]
            local = parts[4]
            extra_steps += parts[6]
            ratios.append(parts[7])
            if local > best_local:
                best_local = max(local, best_local)
                bl_round = cur_step
            high_score = max(score, high_score)

    average_ratio = avg(ratios)
    print 'Accumulated reward: {0}'.format(accumulated_reward)
    print 'Best local reward: {0} in round {1}'.format(best_local, bl_round)
    print 'Total deaths: {0}'.format(deaths)
    print 'Total timeouts: {0}'.format(timeouts)
    print 'High Score: {0}'.format(high_score)
    print 'Total extra steps: {0}'.format(extra_steps)
    print 'Average performance: {0}'.format(average_ratio)
    magic = ((accumulated_reward - extra_steps * 0.2 - timeouts * 10 - deaths) / (extra_steps)) * average_ratio 
#   magic = ((best_local * 2 - deaths * 3) * (high_score + accumulated_reward / high_score) * 0.001 + (high_score * 0.001) - extra_steps * 0.001 - timeouts) * average_ratio
    print 'Evaluation score: {0}'.format(magic)
    print '\t',
#   if magic < 100 or timeouts > 100 or accumulated_reward < 0 or average_ratio < 0.3:
    if magic <= 0.01:
        print 'FAIL'
    else:
        print 'PASS'
    return (accumulated_reward, best_local, bl_round, deaths, timeouts, extra_steps, average_ratio, high_score, magic)

def summarize(name):
    print '========================'
    print '{0} summary:'.format(name)
    best_average = 0
    best_local = 0
    ba_round = 0
    bl_round = 0
    deaths = 0
    timeouts = 0
    with open(name, 'r') as f:
        text = f.read()
        for cur_round, line in enumerate(text.splitlines()):
            parts = map(float, line.split(',')) # round eff, deaths, average, cumul, local
            round_deaths = parts[1]
            average = parts[2]
            local = parts[4]
            if average > best_average and cur_round > 50:
                best_average = max(average, best_average)
                ba_round = cur_round
            if local > best_local:
                best_local = max(local, best_local)
                bl_round = cur_round
            if round_deaths == -1:
                timeouts += 1
            else:
                deaths += round_deaths

    print 'Best average: {0} in round {1}'.format(best_average, ba_round)
    print 'Best local reward: {0} in round {1}'.format(best_local, bl_round)
    print 'Total deaths: {0}'.format(deaths)
    print 'Total timeouts: {0}'.format(timeouts)
    return (best_average, ba_round, best_local, bl_round, deaths, timeouts)

def make_plot(bav, bar, blv, blr, dts, tos):
    raise Exception('Not implemented')

def main():
    global args
    for fn in args.names:
        data = summarize_e(fn)
        if args.plot:
            make_plot(*data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph plotter')
    parser.add_argument('names', nargs='+', help='input file name(s)')
#   parser.add_argument('--plot', help='plot results')
    args = parser.parse_args()
    args.plot = None
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except Exception as e:
        print 'error', e
        raise

