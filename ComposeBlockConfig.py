import random as rd

from MARS_CI.DataTypes import SetType
from MARS_CI.Parser import parse_log
from Universal.Analyze.FindMax import get_top
from Universal.DataTypes import NpArray

##################################################
# Automatic block config composer by aryavorskiy #
# Input: MARS_CI full log                        #
# Output: Short summary, block file, link file   #
##################################################

while True:
    sets = parse_log(input('Filename? ')).select_type(SetType.DEPENDENT)

    directing_trajectories_n = int(input('How many directing trajectories? '))
    directing_sets = [a[0] for a in
                      get_top(sets, directing_trajectories_n // 2, lambda x, y: x.hamiltonian < y.hamiltonian)]
    print('Hamiltonian from {} to {}; temperature from {} to {}'.
          format(directing_sets[0].hamiltonian, directing_sets[-1].hamiltonian, directing_sets[0].start_temperature,
                 directing_sets[1].start_temperature))

    directing_sources = []
    for set_info in directing_sets:
        if set_info.initial_spins not in directing_sources and set_info.initial_spins * -1 not in directing_sources:
            directing_sources.append(set_info.initial_spins)

    random_counter = 0
    while len(directing_sources) < directing_trajectories_n:
        new_set = [rd.uniform(-1, 1) for i in range(len(directing_sources[0]))]
        directing_sources.append(NpArray(new_set))
        random_counter += 1
    dependent_trajectories_n = int(input('How many dependent trajectories? '))
    print(
        f'Block contains {len(directing_sources)} directing ({len(directing_sources) - random_counter} loaded, ' +
        f'{random_counter} random) and {dependent_trajectories_n} dependent trajectories')

    writer = open(input('Where to write block? '), 'w')
    writer.write(f'{dependent_trajectories_n + len(directing_sources)}\n')
    for directing_source in directing_sources:
        for spin in directing_source:
            writer.write(f'{spin} ')
        writer.write('\n')
    writer.write('RAND\n' * dependent_trajectories_n)
    writer.close()

    writer = open(input('Where to write link? '), 'w')
    writer.write(f'{dependent_trajectories_n + len(directing_sources)}\n')
    writer.write('NONE\n' * len(directing_sources))
    writer.write('{}\n'.format(' '.join([str(a) for a in list(range(len(directing_sources)))])) *
                 dependent_trajectories_n)
    writer.close()
    print()
