from Modules import Plot
from Modules.Analyze.FindMax import analyze_set_top
from Modules.Parse.OutputParser import parse_output

####################################################################
# Automatic temperature-hamiltonian diagram plotter by aryavorskiy #
# Input: MARS_CI output file                                       #
# Output: Short summary, diagram image                             #
####################################################################

while True:
    title = input('Title? ')
    pl = Plot.Plot(title)
    data = parse_output(input('Filename? '))

    pl.add_plot_data((data[3], data[0]), 'b^', legend='Directing runs')
    print('Analyzing directing runs:')
    analyze_set_top(data[0], 5)

    pl.add_plot_data((data[4], data[1]), 'ro', legend='Dependent runs')
    print('Analyzing dependent runs:')
    analyze_set_top(data[1], 10)
    pl.plot_all()
