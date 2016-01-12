#!/usr/bin/python2
import argparse
import operator
#import numpy as np
from bokeh.plotting import figure, output_file, save, show
from bokeh.models import LinearAxis, Range1d

def get_data(fn):
    def insert(cols, index, item):
        try:
            cols[index].append(item)
        except IndexError:
            cols.append([item])
    with open(fn, 'r') as f:
        cols = []
        for line in f.readlines():
            elements = map(float, line.strip().split(','))
            for eno, epart in enumerate(elements):
                insert(cols, eno, epart)
    return cols

def get_y(fn):
    data = []
    with open(fn, 'r') as f:
        points = []
        highs  = []
        local  = []
        for line in f.readlines():
            elements = map(float, line.strip().split(','))
            points.append(elements[0])
            highs.append(elements[1])
            local.append(elements[2])
            
        data.append(points)
        data.append(highs)
        data.append(local)
    return data

def get_y_b(fn):
    data = []
    with open(fn, 'r') as f:
        steps = []
        deaths = []
        avgs = []
        accumul = []
        accumu2 = []
        for line in f.readlines():
            elements = map(float, line.strip().split(','))
            steps.append(elements[0])
            deaths.append(elements[1])
            avgs.append(elements[2])
            accumul.append(elements[3])
            accumu2.append(elements[4])
            
        data.append(steps)
        data.append(deaths)
        data.append(avgs)
        data.append(accumul)
        data.append(accumu2)
    return data

def get_range(name, index=3):
    with open(name, 'r') as f:
        low = 0
        high = 0
        for line in f.readlines():
            part = map(float, line.strip().split(','))[index]
            if part > high:
                high = part
            if part < low:
                low = part
    return low, high

def evaluation_plot(fn, display=True):
    base_fn = fn[:fn.find('.txt')]
    output_file(base_fn + '.html', title=base_fn)
    y = get_data(fn)
    x = range(len(y[0]))
    p = figure(title=base_fn, x_axis_label='evaluation', y_axis_label='score', plot_width=1000)
    p.circle(x, y[6], color='teal', learning_rate=0.5, size=3)      # extra steps
#   p.circle(x, y[0], color='teal', learning_rate=0.5, size=0.5)    # score
    p.circle(x, y[5], color='red', learning_rate=0.5, size=0.5)     # deaths/round
    p.circle(x, y[2], color='black', learning_rate=0.5, size=0.5)   # timeouts (total)
#   p.circle(x, y[3], color='blue', learning_rate=0.5, size=0.5)    # accumul. reward
    p.circle(x, y[4], color='orange', learning_rate=0.9, size=0.5)  # local reward

    if display:
        show(p)
    else:
        save(p)

def counter_plot(fn, display=True):
    base_fn = fn[:fn.find('.txt')]
    output_file(base_fn + '.html', title=base_fn)
    y = get_data(fn)
    x = range(len(y[0]))
    p = figure(title=base_fn, x_axis_label='evaluation', y_axis_label='amount', plot_width=1000)
    p.extra_y_ranges = {'reward': Range1d(start=0, end=max(y[3])*1.05), 'ratio': Range1d(start=0, end=1.1)}
    p.add_layout(LinearAxis(y_range_name='reward'), 'right')
    p.add_layout(LinearAxis(y_range_name='ratio'), 'left')
#  p.add_layout(LinearAxis(y_range_name='ratio'), 'right')
#   p.circle(x, y[6], color='teal', learning_rate=0.5, size=3)      # extra steps
#   p.circle(x, y[0], color='teal', learning_rate=0.5, size=0.5)    # score
    p.circle(x, y[1], color='red', learning_rate=0.8, size=2)     # deaths
    p.circle(x, y[2], color='black', learning_rate=0.8, size=2)   # timeouts 
    p.triangle(x, y[7], color='black', learning_rate=1, size=5, y_range_name='ratio')    # ratio
    p.triangle(x, y[8], color='teal', learning_rate=1, size=5, y_range_name='ratio')    # performance
    p.line(x, y[3], color='blue', line_width=1, y_range_name='reward')    # accumul. reward
    p.y_range = Range1d(0, max(max(y[1]),max(y[2]))*1.10)

    if display:
        show(p)
    else:
        save(p)

def pong_plot(fn, display=True):
    base_fn = fn[:fn.find('.txt')]
    output_file(base_fn + '.html', title=base_fn)
    y = get_data(fn)
    x = range(len(y[0]))
    p = figure(title=base_fn, x_axis_label='evaluation', y_axis_label='count', plot_width=1000)
    p.line(x, y[0], color='teal', learning_rate=0.8)    # wins
    p.line(x, y[1], color='red', learning_rate=0.4)     # losses
    p.y_range = Range1d(0, max(max(y[1]),max([0]))*1.10)

    if display:
        show(p)
    else:
        save(p)

def compare_evals(fn1, fn2):
    assert fn1, 'fn1 is a {0}'.format(type(fn1))
    assert fn2, 'fn2 is a {0}'.format(type(fn2))
    base_fn = fn1[:fn1.find('.txt')], fn2[:fn2.find('.txt')]
    title=base_fn[0] + ' vs ' + base_fn[1]
    output_file(base_fn[0][base_fn[0].find('/')+1:]+'vs'+base_fn[1][base_fn[1].find('/')+1:]+'.html', title=title)
    y1 = get_data(fn1)
    y2 = get_data(fn2)
    x = range(len(y1[0]))
    colors = ['teal', 'orange']
    p = figure(title=title, x_axis_label='evaluation', y_axis_label='score', plot_width=1000)
    p.circle(x, y1[6], color=colors[0], learning_rate=0.5, size=3)
    p.circle(x, y2[6], color=colors[1], learning_rate=0.5, size=3)
    p.triangle(x, y1[5], color=colors[0], learning_rate=0.3, size=2)
    p.triangle(x, y2[5], color=colors[1], learning_rate=0.3, size=2)
    p.inverted_triangle(x, y1[2], color=colors[0], learning_rate=0.3, size=2)
    p.inverted_triangle(x, y2[2], color=colors[1], learning_rate=0.3, size=2)
    p.line(x, y1[4], color=colors[0], learning_rate=0.5, size=0.5)
    p.line(x, y2[4], color=colors[1], learning_rate=0.5, size=0.5)
    show(p)

def bench_plot():
    name1 = args.name[0]
    wname = name1[:name1.find('txt')] + 'html' 
    output_file(wname, title=wname)
    p = figure(title=wname, x_axis_label='iteration', y_axis_label='score', plot_width=1000)
    therange = get_range(name1, index=3)
    therange2 = get_range(name1, index=4)
    p.extra_y_ranges = {'deaths': Range1d(start=-0.1, end=10), 'reward': Range1d(start=therange[0], end=therange[1]), 'reward2': Range1d(start=therange2[0], end=therange2[1]*1.1)}
    p.add_layout(LinearAxis(y_range_name='reward'), 'right')
    p.add_layout(LinearAxis(y_range_name='reward2'), 'left')
    if len(args.name) == 1:
        for fn in reversed(args.name):
            color = 'blue'
            if fn == name1: color = 'teal'
            y = get_y_b(fn)
            x = range(len(y[0]))
#           p.triangle(x, y[0], line_width=1, line_color=color)
            p.circle(x, y[0], color=color, learning_rate=0.5, size=0.5)
    color = []
    color.append(['red', 'orange', 'blue'])
    color.append(['green', 'yellow', 'red'])
    color.append(['blue', 'magenta', 'orange'])
    color.append(['orange', 'cyan', 'magenta'])
    color.append(['yellow', 'red', 'cyan'])
    color.append(['black', 'black', 'black'])
    color.append(['pink', 'pink', 'pink'])
    for i, fn in enumerate(args.name):
        add = float(len(args.name) - i) * 0.1
        y = get_y_b(fn)
        deaths = [ (0 if pp == 0 else pp+add) for pp in y[1] ]
        x = range(len(y[0]))
#       zp = np.poly1d(np.polyfit(x, y[2], 1))
#       z = list([zp(aa) for aa in x])
        p.line(x, y[4], line_width=1, line_color=color[i][2], line_learning_rate=0.45, y_range_name='reward2')
        p.line(x, deaths, line_width=1, line_color=color[i][0], y_range_name='deaths')
        p.line(x, y[2], line_width=1, line_color=color[i][1])
        p.line(x, y[3], line_width=2, line_color=color[i][2], y_range_name='reward')
#       p.line(x, z, line_width=2, line_color=color[i][0])
    p.y_range = Range1d(0, 1.1)
    save(p)

def main():
    fname = args.name[0]
    name = fname[:fname.find('txt')]
    yname = args.yname
    y = get_y(fname)
    x = range(len(y[0]))
    x = [(1+r) for r in x]
    output_file(name+'html', title=name[:-1])
    p = figure(title=name, x_axis_label='moves made', y_axis_label='score') 
#   p.extra_y_ranges = {'score': Range1d(start=0, end=100), 'avg': Range1d(start=0, end=max(map(float,y[0]))) }
    p.line(x, y[0], legend="score", line_width=2,# y_range_name='score',
            line_color='red')
#           color='red')
    p.triangle(x, y[1], legend="high", line_width=2)
    p.triangle(x, y[2], legend="local high", line_width=2, color='orange')
#   p.line(x, map(float, y[0]), legend="average", line_width=2, y_range_name='avg', line_color='orange')
#   p.line(x, map(float, y[2]), legend="high", line_width=2, y_range_name='avg')
#   p.add_layout(LinearAxis(y_range_name='avg'), 'right')
    save(p)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='graph plotter')
    parser.add_argument('name', nargs='+', help='input file name')
    parser.add_argument('-a', '--yname', default='y-axis', help='y-axis name')
    parser.add_argument('-b', '--benchmark', action='store_true', help='plot benchmarking data')
    args = parser.parse_args()
    try:
        if args.benchmark:
            bench_plot()
        else:
            main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except Exception as e:
        print 'error', e
        raise

