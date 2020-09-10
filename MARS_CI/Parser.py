import numpy as np

from MARS_CI.DataTypes import BlockInfo, LogInfo, SetType
from Universal.DataTypes import NpArray
from Universal.Utils import file_length, print_progressbar


def parse_auto(file, verbose=True):
    """
    Parse arbitrary file produce by MARS_CI. Type will be detected automatically.

    :param file: Name of file to parse
    :param verbose: Show progressbar if true
    :return: List of BlockInfo objects
    """
    first_line = open(file).__next__()
    if first_line.startswith('-------') or first_line.startswith('t e'):
        return parse_output(file, verbose)
    elif first_line.startswith('Started'):
        return parse_log(file, verbose)
    else:
        raise ValueError('Invalid file type')


def parse_output(output_file, verbose=True):
    """
    Parse output file produced by MARS_CI.

    :param output_file: Name of file to parse
    :param verbose: Show progressbar if true
    :return: List of BlockInfo objects
    """
    file_len = file_length(output_file)
    line_no = 0
    blocks = []
    for line in open(output_file):
        line_no += 1
        if verbose:
            print_progressbar(line_no, file_len, prefix='Parsing output...')
        try:
            temp = float(line.split()[0])
        except ValueError:
            continue  # Invalid line start
        except IndexError:
            continue  # Empty line

        block = BlockInfo(temp)

        for word in line.split()[1:]:  # Ignore first column
            try:
                if word[0] == '(' and word[-1] == ')':
                    block.append_set(hamiltonian=float(word[1:-1]), set_type=SetType.NO_ANNEAL)
                elif word[0] == '<' and word[-1] == '>':
                    block.append_set(hamiltonian=float(word[1:-1]), set_type=SetType.INDEPENDENT)
                else:
                    block.append_set(hamiltonian=float(word), set_type=SetType.DEPENDENT)
            except ValueError:
                break
        blocks.append(block)
    return LogInfo(blocks)


def parse_log(log_file, preserve_initial_spins=True, verbose=True):
    """
    Parse log file produced by MARS_CI.

    :param log_file: Name of file to parse
    :param preserve_initial_spins: Set to true to discard initial spin values to spare RAM
    :param verbose: Show progressbar if true
    :return: List of BlockInfo objects
    """
    file_len = file_length(log_file)
    line_no = 0
    blocks = []
    file_reader = open(log_file)
    line = file_reader.__next__()
    line_no += 1
    while True:
        if verbose:
            print_progressbar(line_no, file_len, prefix='Parsing log...')
        if line.startswith('Started') or line.startswith('Finished'):
            processing_start = line.startswith('Started')
            if processing_start:
                block = BlockInfo(float(line.split()[5][:-1]))
            else:
                block = BlockInfo(float(line.split()[6][:-1]), steps=int(line.split()[8]))
            while True:
                try:
                    line = file_reader.__next__()
                    line_no += 1
                except StopIteration:
                    break
                if line.startswith('Set'):  #
                    set_type = None
                    try:
                        hamiltonian = float(line.split()[3][:-1])
                    except ValueError:
                        set_type = line.split()[3][:-1]
                        hamiltonian = float(line.split()[5][:-1])
                    spins = NpArray([float(spin) for spin in file_reader.__next__().split()], dtype=np.float16)
                    line_no += 1
                    if processing_start:
                        block.append_set(**{
                            'initial_spins': spins if preserve_initial_spins or not processing_start else None,
                            'set_type': set_type
                        })
                    else:
                        block.append_set(**{
                            'hamiltonian': hamiltonian,
                            'spins': spins,
                            'set_type': set_type
                        })
                elif line == '\n':
                    pass
                else:
                    break
            if processing_start:
                blocks.append(block)
            else:
                for i in range(len(blocks)):
                    if block == blocks[i]:
                        blocks[i].merge(block)
                        break
                else:
                    raise AssertionError("This shouldn't have happened")
        else:
            try:
                line = file_reader.__next__()
                line_no += 1
            except StopIteration:
                break
    return LogInfo(blocks)
