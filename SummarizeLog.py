from Modules.Analyze.FindMax import get_top, verbose_top
from Modules.Parse.LogParser import parse_log, split_log_data_by_sets

##################################################
# Automatic log analyzer by aryavorskiy          #
# Input: MARS_CI log file, filename to save data #
# Output: Informative summary                    #
##################################################

log_data = split_log_data_by_sets(parse_log(input('Filename? ')))
target_filename = input('Target filename? (\'n\' if you do not want to export to file) ')
target_filename = None if target_filename == 'n' else target_filename
top_data = get_top(log_data, 10, lambda x, y: x.hamiltonian < y.hamiltonian)
for record in top_data:
    record[0] = str(record[0])
verbose_top(top_data)
if target_filename is not None:
    verbose_top(top_data, filename=target_filename)
