from Modules import Plot
from Modules.Analyze.FindMax import analyze_set_top
from Modules.Analyze.Histogram import get_histogram, get_bounds
from Modules.Parse.OutputParser import parse_output

##########################################################
# Automatic hamiltonian histogram plotter by aryavorskiy #
# Input: MARS_CI output file                             #
# Output: Short summary, histogram image                 #
##########################################################

while True:
    title = input('Title? ')
    pl = Plot.Plot(title)
    data = parse_output(input('Filename? '))
    bounds = get_bounds(data[1])
    print('Graph xrange set to {}'.format(bounds))

    histo_indep = get_histogram(data[0], *bounds, 100, mode='curve')
    pl.add_plot_data(histo_indep, 'b-', legend='Directing runs')
    print('Analyzing directing runs:')
    analyze_set_top(data[0], 5)

    histo_dep = get_histogram(data[1], *bounds, 100, mode='curve')
    pl.add_plot_data(histo_dep, 'r-', legend='Dependent runs')
    print('Analyzing dependent runs:')
    analyze_set_top(data[1], 10)
    pl.plot_all()
