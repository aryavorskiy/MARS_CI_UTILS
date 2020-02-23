from MARS_CI.Parser import parse_log
from Universal.Analyze.FindMax import get_top

##################################################
# Automatic block config composer by aryavorskiy #
# Input: MARS_CI full log                        #
# Output: Short summary, block file, link file   #
##################################################

while True:
    sets = [set_info for block in parse_log(input('Filename? ')) for set_info in block]
    top_size = int(input('How many directing trajectories? '))
    top_data = [a[0] for a in get_top(sets, top_size, lambda x, y: x.hamiltonian < y.hamiltonian)]
    directing_sources = []
    print('Hamiltonian from {} to {}; temperature from {} to {}'.
          format(top_data[0].hamiltonian, top_data[-1].hamiltonian, top_data[0].start_temperature,
                 top_data[1].start_temperature))
    for top_record in top_data:
        if top_record.initial_spins not in directing_sources:
            directing_sources.append(top_record.initial_spins)
            directing_sources.append(top_record.initial_spins * -1)
    dependent_trajectories = int(input('How many dependent trajectories? '))
    print(f'Block contains {len(directing_sources)} directing and {dependent_trajectories} dependent trajectories')

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
    print()
