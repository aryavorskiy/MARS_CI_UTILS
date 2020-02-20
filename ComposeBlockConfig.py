from Modules.Analyze.FindMax import get_top
from Modules.Parse.LogParser import parse_log, split_log_data_by_sets

##################################################
# Automatic block config composer by aryavorskiy #
# Input: MARS_CI full log                        #
# Output: Short summary, block file, link file   #
##################################################

while True:
    not_simplified_data = parse_log(input('Filename? '))
    simplified_data = split_log_data_by_sets(not_simplified_data)
    top_size = 4
    top_data = get_top(simplified_data, top_size, lambda x, y: x.hamiltonian < y.hamiltonian)
    top_data = [a[0] for a in top_data]
    directing_sources = []
    temperatures = [ds.start_temperature for ds in top_data]
    print('Hamiltonian from {} to {}; temperature from {} to {}'.
          format(top_data[0].hamiltonian, top_data[-1].hamiltonian, temperatures[0], temperatures[-1]))
    for top_record in top_data:
        if top_record.initial_spins not in directing_sources:
            directing_sources.append(top_record.initial_spins)
            directing_sources.append(top_record.initial_spins * -1)
    dependent_trajectories = 10

    writer = open(input('Where to write block? '), 'w')
    writer.write(f'{dependent_trajectories + len(directing_sources)}\n')
    for directing_source in directing_sources:
        for spin in directing_source:
            writer.write(f'{spin} ')
        writer.write('\n')
    writer.write('RAND\n' * dependent_trajectories)
    writer.close()

    writer = open(input('Where to write link? '), 'w')
    writer.write(f'{dependent_trajectories + len(directing_sources)}\n')
    writer.write('NONE\n' * len(directing_sources))
    writer.write('{}\n'.format(' '.join([str(a) for a in list(range(len(directing_sources)))])) *
                 dependent_trajectories)
    writer.close()
