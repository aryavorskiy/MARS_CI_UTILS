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
    blocks = parse_auto(input('Filename? '))
    temp_dir = [set_info.start_temperature for block in blocks for set_info in block if
                set_info.set_type == 'Independent']
    temp_dep = [set_info.start_temperature for block in blocks for set_info in block if
                set_info.set_type == 'Dependent']
    ham_dir = [set_info.hamiltonian for block in blocks for set_info in block if set_info.set_type == 'Independent']
    ham_dep = [set_info.hamiltonian for block in blocks for set_info in block if set_info.set_type == 'Dependent']

    pl.add_plot_data((temp_dir, ham_dir), 'b^', legend='Directing runs')
    print('Analyzing directing runs:')
    analyze_set_top(ham_dir, 5)

    pl.add_plot_data((temp_dep, ham_dep), 'ro', legend='Dependent runs')
    print('Analyzing dependent runs:')
    analyze_set_top(ham_dep, 10)
    pl.plot_all()
    print()
