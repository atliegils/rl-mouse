#!/usr/bin/python2
import os
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

def counter_plot(fn, display=True):
    base_fn = fn[:fn.find('.txt')]
    output_file(base_fn + '.html', title=base_fn)
    deaths, timeouts, ratio, accumulated, extra_steps = get_data(fn)
    x = range(len(deaths))
    p = figure(title=base_fn, x_axis_label='evaluation', y_axis_label='count', plot_width=1000)
    p.extra_y_ranges = {'reward': Range1d(start=min(0, min(accumulated)*1.05), end=max(0, max(accumulated)*1.05)), 'ratio': Range1d(start=0, end=1.1)}
    p.add_layout(LinearAxis(y_range_name='reward', axis_label='reward'), 'right')
    p.add_layout(LinearAxis(y_range_name='ratio', axis_label='ratio'), 'left')
    # p.circle(x, extra_steps, color='teal', alpha=0.5, size=3, legend='+steps')      # extra steps
    # p.circle(x, score, color='teal', alpha=0.5, size=0.5, legend='score')    # score
    p.circle(x, deaths, color='red', alpha=0.8, size=5, legend='deaths')     # deaths
    p.square(x, timeouts, color='blue', alpha=0.8, size=5, legend='timeouts')   # timeouts
    p.triangle(x, ratio, color='black', alpha=1, size=5, y_range_name='ratio', legend='ratio')    # ratio
    # p.triangle(x, performance, color='teal', alpha=1, size=5, y_range_name='ratio', legend='performance')    # performance
    p.line(x, accumulated, color='blue', y_range_name='reward', legend='reward')    # accumul. reward
    p.y_range = Range1d(0, max(max(deaths),max(timeouts),1)*1.10)
    p.x_range = Range1d(0, int(1.2*len(x))) # create room for legend

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
    p.line(x, y[0], color='teal', alpha=0.8)    # wins
    p.line(x, y[1], color='red', alpha=0.4)     # losses
    p.y_range = Range1d(0, max(max(y[1]),max([0]))*1.10)

    if display:
        show(p)
    else:
        save(p)

def compare_evals(fn1, fn2):
    assert fn1, 'fn1 is a {0}'.format(type(fn1))
    assert fn2, 'fn2 is a {0}'.format(type(fn2))
    base_fn = fn1[1+fn1.rfind(os.sep):fn1.find('.txt')], fn2[1+fn2.rfind(os.sep):fn2.find('.txt')]
    title=base_fn[0] + ' vs ' + base_fn[1]
    y1 = get_data(fn1)
    y2 = get_data(fn2)
    accumulated = []
    accumulated.extend(y1[3])
    accumulated.extend(y2[3])
    deaths = []
    deaths.extend(y1[0])
    deaths.extend(y2[0])
    timeouts = []
    timeouts.extend(y1[1])
    timeouts.extend(y2[1])
    output_file('comparisons'+os.sep+title+'.html', title=title)
    x = range(min(len(y1[0]), len(y2[0])))
    colors = ['teal', 'orange']
    p = figure(title=title, x_axis_label='evaluation', y_axis_label='count', plot_width=1000)
    p.extra_y_ranges = {'reward': Range1d(start=min(0, min(accumulated)*1.05), end=max(0, max(accumulated)*1.05)), 'ratio': Range1d(start=0, end=1.1)}
    p.add_layout(LinearAxis(y_range_name='reward', axis_label='reward'), 'right')
    p.add_layout(LinearAxis(y_range_name='ratio', axis_label='ratio'), 'left')
    p.circle(x, y1[0], color='red', alpha=0.8, size=5, legend='deaths1')     # deaths
    p.square(x, y1[1], color='blue', alpha=0.8, size=5, legend='timeouts1')   # timeouts
    p.triangle(x, y1[2], color='black', alpha=1, size=5, y_range_name='ratio', legend='ratio1')    # ratio
    p.line(x, y1[3], color='blue', y_range_name='reward', legend='reward1')    # accumul. reward
    p.circle(x, y2[0], color='green', alpha=0.8, size=5, legend='deaths2')     # deaths
    p.square(x, y2[1], color='orange', alpha=0.8, size=5, legend='timeouts2')   # timeouts
    p.triangle(x, y2[2], color='teal', alpha=1, size=5, y_range_name='ratio', legend='ratio2')    # ratio
    p.line(x, y2[3], color='orange', y_range_name='reward', legend='reward2')    # accumul. reward
    p.y_range = Range1d(0, max(max(deaths),max(timeouts),1)*1.10)
    p.x_range = Range1d(0, int(1.2*len(x))) # create room for legend
    show(p)

