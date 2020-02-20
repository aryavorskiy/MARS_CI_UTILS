import numpy as np

from Modules.DataTypes import NpArray, SetInfo
from Modules.ParseExtensions import file_length, print_progressbar


def parse_log(log_file, preserve_initial_spins=True, verbose=True):
    """
    Parse log file produced by MARS_CI.

    :param log_file: Name of file to parse
    :param preserve_initial_spins: Set to true to discard initial spin values to spare RAM
    :param verbose: Show progressbar if true
    :return: List of dicts, each dict represents block info
    """
    file_len = file_length(log_file)
    line_no = 0
    block_starts = []
    block_finishes = []
    file_reader = open(log_file)
    line = file_reader.__next__()
    line_no += 1
    while True:
        if verbose:
            print_progressbar(line_no, file_len, prefix='Parsing log...')
        if line.startswith('Started') or line.startswith('Finished'):
            processing_start = line.startswith('Started')
            if processing_start:
                block_info = {'temperature': float(line.split()[5][:-1])}
            else:
                block_info = {'temperature': float(line.split()[6][:-1]), 'steps': int(line.split()[8])}
            block_data = []
            while True:
                try:
                    line = file_reader.__next__()
                    line_no += 1
                except StopIteration:
                    break
                if line.startswith('Set'):  #
                    set_type = 'Undefined'
                    try:
                        hamiltonian = float(line.split()[3][:-1])
                    except ValueError:
                        set_type = line.split()[3][:-1]
                        hamiltonian = float(line.split()[5][:-1])
                    spins = NpArray([float(spin) for spin in file_reader.__next__().split()], dtype=np.float16)
                    line_no += 1
                    block_data.append({
                        'ham': hamiltonian,
                        'spins': spins if preserve_initial_spins or not processing_start else None,
                        'type': set_type
                    })
                elif line == '\n':
                    pass
                else:
                    break
            if processing_start:
                block_info.update(start_data=block_data)
                block_starts.append(block_info)
            else:
                block_info.update(finish_data=block_data)
                block_finishes.append(block_info)
        else:
            try:
                line = file_reader.__next__()
                line_no += 1
            except StopIteration:
                break
    for i in range(len(block_starts)):
        for fin_rec in block_finishes:
            if block_starts[i]['temperature'] == fin_rec['temperature']:
                block_starts[i].update(fin_rec)
                block_finishes.remove(fin_rec)
                break
    if verbose:
        print()
    return block_starts


def split_log_data_by_sets(data):
    """
    Converts list with block infos into list with set infos stored in special object files.

    :param data: List with block infos produced by parse_log method
    :return: List of SetInfo objects
    """
    simplified_data = []
    for record in data:
        size = len(record['start_data'])
        for i in range(size):
            try:
                simplified_data.append(
                    SetInfo(
                        record['temperature'],
                        record['finish_data'][i]['spins'],
                        record['finish_data'][i]['ham'],
                        record['steps'],
                        record['finish_data'][i]['type'],
                        record['start_data'][i]['spins']
                    ))
            except TypeError:
                pass
            except KeyError:
                pass
    return simplified_data


def sort_data_by_type(split_data: list):
    """
    Sorts SetInfo objects by type: Independent, No-anneal, Dependent or Undefined.

    :param split_data: List of SetInfo objects
    :return: Dict with different types as keys and lists with SetInfo objects as values
    """
    sorted_data = {}
    for set_info in split_data:
        if set_info.set_type in sorted_data:
            sorted_data[set_info.set_type].append(set_info)
        else:
            sorted_data.update({set_info.set_type: [set_info]})
    return sorted_data
