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
    score, deaths, timeouts, accumulated, _, local_deaths, extra_steps, ratio, _ = get_data(fn)
    x = range(len(score))
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
    base_fn = fn1[:fn1.find('.txt')], fn2[:fn2.find('.txt')]
    title=base_fn[0] + ' vs ' + base_fn[1]
    y1 = get_data(fn1)
    y2 = get_data(fn2)
    output_file('comparisons'+os.sep+base_fn[0][base_fn[0].find(os.sep)+1:]+'vs'+base_fn[1][base_fn[1].find(os.sep)+1:]+'.html', title=title)
    x = range(len(y1[0]))
    colors = ['teal', 'orange']
    p = figure(title=title, x_axis_label='evaluation', y_axis_label='score', plot_width=1000)
    p.extra_y_ranges = {'reward': Range1d(start=min(0, min(y1[4]), min(y2[4]))*1.05, end=max(0, max(y1[4]), max(y2[4]))*1.05)}
    p.add_layout(LinearAxis(y_range_name='reward', axis_label='reward'), 'right')
    p.circle(x, y1[6], color=colors[0], alpha=0.5, size=3)
    p.circle(x, y2[6], color=colors[1], alpha=0.5, size=3)
    p.triangle(x, y1[5], color=colors[0], alpha=0.3, size=2)
    p.triangle(x, y2[5], color=colors[1], alpha=0.3, size=2)
    p.inverted_triangle(x, y1[2], color=colors[0], alpha=0.3, size=2)
    p.inverted_triangle(x, y2[2], color=colors[1], alpha=0.3, size=2)
    p.line(x, y1[4], color=colors[0], alpha=0.5, y_range_name='reward')
    p.line(x, y2[4], color=colors[1], alpha=0.5, y_range_name='reward')
    show(p)
