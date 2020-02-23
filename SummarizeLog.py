from MARS_CI.Parser import parse_auto
from Universal.Analyze.FindMax import get_top, verbose_top

##################################################
# Automatic log analyzer by aryavorskiy          #
# Input: MARS_CI log file, filename to save data #
# Output: Informative summary                    #
##################################################

while True:
    sets = [set_info for block in parse_auto(input('Filename? ')) for set_info in block
            if set_info.set_type in ('Dependent', None)]
    print()
    temperature_list = [set_info.start_temperature for set_info in sets]
    print(f'Temperature bounds: from {min(temperature_list)} to {max(temperature_list)}')
    top_data = get_top(sets, 10, lambda x, y: x.hamiltonian < y.hamiltonian)
    for record in top_data:
        record[0] = str(record[0])
    verbose_top(top_data)
    print()
