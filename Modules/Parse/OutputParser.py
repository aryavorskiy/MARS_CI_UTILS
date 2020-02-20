from Modules.DataTypes import NpArray
from Modules.ParseExtensions import file_length, print_progressbar


def parse_output(file, verbose=True):
    """
    Parse output file produced by MARS_CI.
    :param file: Filename to read
    :param verbose: Set
    :return: Tuple of 6 arrays.
     3 hamiltonian lists atd 3 corresponding start temperature lists in the same order
    """
    file_len = file_length(file)
    line_no = 0
    dependent = NpArray([])
    independent = NpArray([])
    no_anneal = NpArray([])
    dependent_temp = NpArray([])
    independent_temp = NpArray([])
    no_anneal_temp = NpArray([])
    for line in open(file):
        line_no += 1
        if verbose:
            print_progressbar(line_no, file_len, prefix='Parsing output...')
        try:
            temp = float(line.split()[0])
        except ValueError:
            continue  # Invalid line start
        except IndexError:
            continue  # Empty line

        for word in line.split()[1:]:  # Ignore first column
            try:
                if word[0] == '(' and word[-1] == ')':
                    no_anneal.append(float(word[1:-1]))
                    no_anneal_temp.append(temp)
                elif word[0] == '<' and word[-1] == '>':
                    independent.append(float(word[1:-1]))
                    independent_temp.append(temp)
                else:
                    dependent.append(float(word))
                    dependent_temp.append(temp)
            except ValueError:
                break
    if verbose:
        print()
    return independent, dependent, no_anneal, independent_temp, dependent_temp, no_anneal_temp
