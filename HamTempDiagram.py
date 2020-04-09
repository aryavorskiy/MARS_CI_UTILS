from MARS_CI.DataTypes import SetType
from MARS_CI.Parser import parse_auto
from Universal import Plot
from Universal.Analyze.FindMax import analyze_set_top

####################################################################
# Automatic temperature-hamiltonian diagram plotter by aryavorskiy #
# Input: MARS_CI output file                                       #
# Output: Short summary, diagram image                             #
####################################################################

while True:
    title = input('Title? ')
    pl = Plot.Plot(title)
    log = parse_auto(input('Filename? '))
    temp_dir, temp_dep = map(log.select_type, [SetType.INDEPENDENT, SetType.DEPENDENT], ['start_temperature'] * 2)
    ham_dir, ham_dep = map(log.select_type, [SetType.INDEPENDENT, SetType.DEPENDENT], ['hamiltonian'] * 2)

    pl.add_plot_data((temp_dir, ham_dir), 'b^', legend='Directing runs')
    print('Analyzing directing runs:')
    analyze_set_top(ham_dir, 5)

    pl.add_plot_data((temp_dep, ham_dep), 'ro', legend='Dependent runs')
    print('Analyzing dependent runs:')
    analyze_set_top(ham_dep, 10)
    pl.plot_all()
    print()
