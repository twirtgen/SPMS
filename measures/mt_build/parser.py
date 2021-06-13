#! /usr/bin/python3

import math
import os

import matplotlib.pyplot as plot
import matplotlib
from matplotlib import rcParams
rcParams['font.family'] = 'serif'
#rcParams['font.size'] = '20'

def parse_and_plot(datafile: str):
    with open(datafile) as fp:
        raw_logs = fp.read()

    raw_data = [[line_data.split(' ')[-1] for line_data in line.split('|')[-1].split(',')][1:] for line in raw_logs.split('\n') if 'mt_manager' in line and 'perf_log' in line]

    print(raw_data)
    print()

    data = {}
    for n_plugins, duration in raw_data:
        try:
            data[n_plugins].append(float(duration))
        except KeyError:
            data[n_plugins] = [float(duration)]
    print(data)
    print()
    for n_plugins, durations in data.items():
        print('%s: %i' % (n_plugins, len(durations)))
    print()

    n_ech = 15 if 't3' in datafile else 20
    print('%s : %i' % (datafile, n_ech))
    cleaned_data = {n_plugins: [i*1000 for i in durations[:n_ech]] for n_plugins, durations in data.items() if len(str(math.log2(int(n_plugins)))) == 3 or n_plugins == 1}
    #cleaned_data = {n_plugins: durations for n_plugins, durations in data.items() if len(str(math.log2(int(n_plugins)))) == 3 or n_plugins == 1}
    print(cleaned_data)

    plot.boxplot(cleaned_data.values(), labels=cleaned_data.keys())
    #plot.xlabel('# plugins [/]', fontsize=16)
    #plot.ylabel('Duration [ms]', fontsize=16)
    plot.title(datafile)
    plot.xlabel('# plugins [/]')
    plot.ylabel('Duration [ms]')

    plot.savefig('plots/%s.pdf' % datafile.split('/')[-1].split('.')[0])
    plot.clf()

    if 't4' in datafile:
        depth = datafile.split('_')[1][-1]
        for n_plugins, durations in cleaned_data.items():
            box_stats = matplotlib.cbook.boxplot_stats(durations)
            line_data = {'med': box_stats[0]['med'], 'min': box_stats[0]['whislo'], 'max': box_stats[0]['whishi']}
            try:
                full_data[depth][n_plugins] = line_data
            except KeyError:
                full_data[depth] = {n_plugins: line_data}
    

if __name__ == '__main__':
    full_data = {}
    for datafile in os.listdir('data'):
        parse_and_plot('data/%s' % datafile)


    plot.clf()

    print()
    print(full_data)
    for depth, depth_data in full_data.items():
        print()
        print(depth_data)
        x = []
        y = []
        min_err = []
        max_err = []
        for n_plugins, values in depth_data.items():
            x.append(n_plugins)
            y.append(values['med'])
            min_err.append(values['med'] - values['min'])
            max_err.append(values['max'] - values['med'])
        print(x)
        print(y)
        plot.errorbar(x, y, yerr=[min_err, max_err], capsize=10, label='depth = %i' % (int(depth)+1))
    plot.ylabel('Duration [ms]')
    plot.xlabel('Number of plugins')
    plot.legend()
    plot.savefig('plots/all.pdf')
