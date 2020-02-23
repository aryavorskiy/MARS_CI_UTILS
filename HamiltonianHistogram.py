from MARS_CI.Parser import parse_auto
from Universal import Plot
from Universal.Analyze.FindMax import analyze_set_top
from Universal.Analyze.Histogram import get_histogram, get_bounds

##########################################################
# Automatic hamiltonian histogram plotter by aryavorskiy #
# Input: MARS_CI output file                             #
# Output: Short summary, histogram image                 #
##########################################################

while True:
    title = input('Title? ')
    pl = Plot.Plot(title)
    blocks = parse_auto(input('Filename? '))
    ham_dir = [set_info.hamiltonian for block in blocks for set_info in block if set_info.set_type == 'Independent']
    ham_dep = [set_info.hamiltonian for block in blocks for set_info in block if set_info.set_type == 'Dependent']
    bounds = get_bounds(ham_dep)
    print('Graph xrange set to {}'.format(bounds))

    histogram_dir = get_histogram(ham_dir, *bounds, 100, mode='curve')
    pl.add_plot_data(histogram_dir, 'b-', legend='Directing runs')
    print('Analyzing directing runs:')
    analyze_set_top(ham_dir, 5)

    histogram_dep = get_histogram(ham_dep, *bounds, 100, mode='curve')
    pl.add_plot_data(histogram_dep, 'r-', legend='Dependent runs')
    print('Analyzing dependent runs:')
    analyze_set_top(ham_dep, 10)
    pl.plot_all()
    print()
