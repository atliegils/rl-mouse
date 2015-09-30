#!/usr/bin/python2
import argparse
import operator
import numpy as np
from bokeh.plotting import figure, output_file, save
from bokeh.models import LinearAxis, Range1d

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
        for line in f.readlines():
            elements = map(float, line.strip().split(','))
            steps.append(elements[0])
            deaths.append(elements[1])
            avgs.append(elements[2])
            accumul.append(elements[3])
            
        data.append(steps)
        data.append(deaths)
        data.append(avgs)
        data.append(accumul)
    return data

def get_range(name):
    with open(name, 'r') as f:
        low = 0
        high = 0
        for line in f.readlines():
            part = map(float, line.strip().split(','))[3]
            if part > high:
                high = part
            if part < low:
                low = part

    return low, high


def bench_plot():
    name1 = args.name[0]
    wname = name1[:name1.find('txt')] + 'html' 
    output_file(wname, title=wname)
    p = figure(title=wname, x_axis_label='iteration', y_axis_label='score', plot_width=1000)
    therange = get_range(name1)
    p.extra_y_ranges = {'deaths': Range1d(start=-0.1, end=10), 'reward': Range1d(start=therange[0], end=therange[1])}
    p.add_layout(LinearAxis(y_range_name='reward'), 'right')
    if len(args.name) == 1:
        for fn in reversed(args.name):
            color = 'blue'
            if fn == name1: color = 'teal'
            y = get_y_b(fn)
            x = range(len(y[0]))
#           p.triangle(x, y[0], line_width=1, line_color=color)
            p.circle(x, y[0], color=color)
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
        zp = np.poly1d(np.polyfit(x, y[2], 1))
        z = list([zp(aa) for aa in x])
        p.line(x, deaths, line_width=1, line_color=color[i][0], y_range_name='deaths')
        p.line(x, y[2], line_width=1, line_color=color[i][1])
        p.line(x, y[3], line_width=2, line_color=color[i][2], y_range_name='reward')
        p.line(x, z, line_width=2, line_color=color[i][0])
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
    parser = argparse.ArgumentParser(description='snake q-learner evaluator')
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

