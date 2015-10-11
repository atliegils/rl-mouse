import argparse

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
        data = summarize(fn)
        if args.plot:
            make_plot(*data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph plotter')
    parser.add_argument('names', nargs='+', help='input file name(s)')
    parser.add_argument('--plot', help='plot results')
    args = parser.parse_args()
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except Exception as e:
        print 'error', e
        raise

