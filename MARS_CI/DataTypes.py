from Universal.DataTypes import NpArray
from Universal.Utils import print_progressbar


class Mat:
    """
    Represents a lattice struct.
    """

    def __init__(self, size=0):
        self.size = size
        self.mat = NpArray([[0.] * size] * size)

    def load_file(self, file: str, verbose=True):
        """
        Loads lattice values from given file.

        :param file: Name of file to read values from
        :param verbose: Show progressbar if true
        :return: None
        """
        reader = open(file)
        first_line = reader.__next__()
        self.size = int(first_line.split()[0])
        if len(first_line.split()) == 1:
            mat = []
            for line in reader:
                if verbose:
                    print_progressbar(len(self.mat), self.size, prefix='Loading lattice...')
                mat.append([float(x) for x in line.split()])
                if len(mat) == self.size:
                    break
            self.mat = NpArray(mat)
        elif len(first_line.split()) == 2:
            for line in reader:
                i, j, val = line.split()
                self.mat[i, j] = self.mat[j, i] = val
        for i in range(self.size):
            for j in range(i):
                self.mat[i, j] = self.mat[j, i]
        if self.size != len(self.mat) or self.size != len(self.mat[0]):
            self.size = 0
            self.mat = NpArray()
            raise ValueError(
                f'Invalid matrix dimensions emerge: {len(self.mat)}x{len(self.mat[0])}, expected {self.size}')

    def load_values(self, mat, linear_element):
        """
        Loads lattice values from two matrices representing the matrix and the linear member.

        :param mat: Matrix values
        :param linear_element: Linear element values
        :return: None
        """
        self.size = len(mat)
        self.mat = NpArray(mat)
        if type(linear_element) in {float, int}:
            for i in range(len(self.mat)):
                self.mat[i, i] = linear_element
        elif hasattr(linear_element, '__iter__'):
            for i in range(len(self.mat)):
                self.mat[i, i] = linear_element[i] if i < len(linear_element) else linear_element[-1]
        else:
            raise TypeError(
                f'Unsupported linear_element type: \'{type(linear_element)}\', expected int, float or iterable')

    def dump(self, filename, export_type):
        """
        Save lattice values in a file

        :param filename: File to save lattice
        :param export_type: Lattice file format: 'lattice' or 'graph'
        :return:
        """
        writer = open(filename, 'w')
        if export_type == 'lattice':
            writer.write(f'{self.size}\n')
            for line in self.mat:
                writer.write(' '.join([str(x) for x in line]) + '\n')
        elif export_type == 'graph':
            # TODO optimize
            writer.write(f'{self.size} {self.size * (self.size + 1) / 2}\n')
            for i in range(self.size):
                for j in range(i + 1, self.size):
                    writer.write(f'{i} {j} {self.mat[i, j]}\n')
        else:
            raise ValueError(f'No export type {export_type} implemented')
        writer.close()

    def hamiltonian(self, spins: iter, type_mat_prod=True):
        """
        Calculates hamiltonian of given spin configuration.

        :param spins: Spin values
        :return: Float value representing hamiltonian
        """
        if len(spins) != self.size:
            raise ValueError('Spin count ({}) does not correspond to mat size ({})'.format(len(spins), self.size))
        hamiltonian = 0.
        for i in range(self.size):
            for j in range(self.size):
                hamiltonian += 0 if (not type_mat_prod and i < j) else self[i, j] * spins[i] * spins[j] if i != j else \
                    spins[i] * self[i, i]
        return hamiltonian

    def is_local_minimum(self, spins: iter, verbose=True):
        """
        Checks if spin configuration is local energy minimum.

        :param spins: Spin values
        :param verbose: Show progressbar if true
        :return: True if spin configuration is a local minimum, false otherwise
        """
        for i in range(self.size):
            if verbose:
                print_progressbar(i, self.size, prefix='Evaluating mean field values...')
            mean_field = sum(self[i, j] * spins[j] for j in range(self.size) if j != i) + self[i, i]
            if mean_field * spins[i] > 0:
                if verbose:
                    print('\r')
                return False
        if verbose:
            print('\r')
        return True

    def __getitem__(self, item):
        """
        Gets lattice element by given indices.

        :param item: Tuple with indices
        :return: Float value representing specified lattice element
        """
        return self.mat[item[0], item[1]]

    def __setitem__(self, idx, value):
        """
        Sets lattice element by given indices to a specified value.

        :param idx: Tuple with indices
        :param value: Value to set
        :return: None
        """
        self.mat[idx[0], idx[1]] = value

    def __eq__(self, other):
        pass


class LogInfo:
    """
    Contains information gathered from single program run
    """

    def __init__(self, blocks):
        """
        :param blocks: List of BlockInfo objects
        """
        self.blocks = blocks

    def select_type(self, set_type, attribute=None):
        """
        Return needed attribute of SetInfo object with specified type.
        :param set_type: SetType object
        :param attribute: String containing needed attribute
        :return: List with attribute objects
        """
        if set_type is None and attribute is None:
            return [set_info for block in self.blocks for set_info in block]
        if set_type is None:
            return [set_info.__dict__[attribute] for block in self.blocks for set_info in block]
        if attribute is None:
            return [set_info for block in self.blocks for set_info in block if
                    set_info.set_type == set_type]
        return [set_info.__dict__[attribute] for block in self.blocks for set_info in block if
                set_info.set_type == set_type]

    def __getitem__(self, item):
        """
        Get temperature slice.
        :param item: Slice object
        :return: Another LogInfo object
        """
        if type(item) == slice:
            if item.step is not None:
                raise ValueError('Invalid temperature slice')
            return LogInfo([block for block in self.blocks if item.start < block.start_temperature < item.stop])
        else:
            raise AssertionError('Not a temperature slice')

    def __iter__(self):
        """
        Get list iterator to achieve backward compatibility.
        :return: List iterator
        """
        return self.blocks.__iter__()


class BlockInfo:
    """
    Represents a block struct
    """

    def __init__(self, start_temperature, steps=None):
        """
        :param start_temperature: Block start temperature
        :param steps: Number of annealing steps required to achieve the result
        """
        self.start_temperature = start_temperature
        self.steps = steps
        self.sets = []

    def append_set(self, **kwargs):
        """
        Add new set to block.

        :param kwargs: Dict with parameters describing a SetInfo object
        :return: None
        """
        if 'start_temperature' in kwargs:
            if kwargs['start_temperature'] != self.start_temperature:
                raise ValueError('Set start temperature does not match block start temperature, unable to add SetInfo')
        else:
            kwargs.update(start_temperature=self.start_temperature)
        if 'steps' in kwargs:
            if kwargs['steps'] != self.start_temperature:
                raise ValueError('Set step count does not match block step count unable to add SetInfo')
        else:
            kwargs.update(steps=self.steps)
        self.sets.append(SetInfo(**kwargs))

    def merge(self, other):
        """
        Merge information from 2 block info objects. Data from parameter object overrides target.

        :param other: Other BlockInfo file
        :return: None
        """
        if type(self) != type(other):
            raise TypeError('Type mismatch: unable to compare {} with {}'.format(
                type(self), type(other)))
        if len(self) != len(other):
            raise ValueError('Block size does not match, unable to merge')
        if self.start_temperature != other.start_temperature:
            raise ValueError('Block start temperatures do not match, unable to merge')
        for i in range(len(self)):
            self.sets[i].merge(other.sets[i])

    def update_set(self, index, set_info):
        """
        Update information about specific set in block.
        Avoid usage if possible.

        :param index: Set index in block
        :param set_info: Object containing required information
        :return: None
        """
        if index >= len(self.sets):
            raise IndexError(f'No set with index {index} in block')
        self.sets[index].merge(set_info)

    def __len__(self):
        """
        :return: Block size
        """
        return len(self.sets)

    def __getitem__(self, item):
        """
        :param item: Index of set in block
        :return: SetInfo object
        """
        return self.sets[item]

    def __eq__(self, other):
        """
        Blocks are considered equal if their start temperatures match.
        :param other: Other BlockInfo file
        :return: Comparison result
        """
        if type(self) != type(other):
            raise TypeError('Type mismatch: unable to compare {} with {}'.format(
                type(self), type(other)))
        return self.start_temperature == other.start_temperature


class SetType:
    """
    Contains possible set_type values
    """
    INDEPENDENT = 'Independent'
    DEPENDENT = 'Dependent'
    NO_ANNEAL = 'No-anneal'
    UNDEFINED = 'Undefined'


class SetInfo:
    """
    Represents a set of spins struct.
    """

    def __init__(self, start_temperature=None, hamiltonian=None, spins=None, steps=None, set_type=None,
                 initial_spins=None):
        """
        :param start_temperature: Set start temperature
        :param spins: Resulting spin values collection
        :param hamiltonian: Resulting hamiltonian
        :param steps: Number of annealing steps required to achieve the result
        :param set_type: Set type - Independent, No-anneal, Dependent or Undefined
        :param initial_spins:
        """
        if start_temperature is None:
            raise ValueError('Start temperature is not defined or null')
        self.start_temperature = float(start_temperature)
        self.hamiltonian = float(hamiltonian) if hamiltonian is not None else None
        self.spins = spins if spins is None or type(spins) == NpArray else NpArray(spins)
        self.steps = steps
        self.set_type = set_type
        self.initial_spins = initial_spins if initial_spins is None or type(initial_spins) == NpArray \
            else NpArray(initial_spins)

    def merge(self, other):
        """
        Merge information from 2 SetInfo objects. Data from parameter object overrides target.

        :param other: Other SetInfo object
        :return: None
        """
        if type(self) != type(other):
            raise TypeError('Type mismatch: unable to compare {} with {}'.format(
                type(self), type(other)))
        if self.start_temperature != other.start_temperature:
            raise ValueError('Set start temperatures do not match, unable to merge')
        if other.hamiltonian is not None:
            self.hamiltonian = other.hamiltonian
        if other.spins is not None:
            self.spins = other.spins
        if other.steps is not None:
            self.steps = other.steps
        if other.initial_spins is not None:
            self.initial_spins = other.initial_spins
        if other.set_type is not None:
            self.set_type = other.set_type

    def __eq__(self, other):
        """
        Compare two SetInfo objects. Two sets considered equal if resulting spin values match.

        :param other: The other SetInfo object to compare with
        :return: Comparison result
        """
        if type(self) != type(other):
            raise TypeError('Type mismatch: unable to compare {} with {}'.format(
                type(self), type(other)))
        if self.hamiltonian != other.hamiltonian:
            return False
        if self.spins is None or other.spins is None:
            return True
        sign_match = self.spins[0] == other.spins[0]
        for i in range(1, len(self.spins)):
            if sign_match ^ (self.spins[i] == other.spins[i]):
                return False
        return True

    def __len__(self):
        return len(self.spins)

    def __str__(self):
        """
        :return: String representation of set info
        """
        return ''.join([
            f'Hamiltonian: {self.hamiltonian}, ',
            f'start temperature: {self.start_temperature}, ',
            f'{self.steps} annealing steps, ' if self.steps is not None else '',
            f'type: {self.set_type}, ' if self.set_type is not None else 'type: Undefined, ',
            f'spins:\n{self.spins}\nInitial spins:\n{self.initial_spins}\n' if self.spins is not None
            else ''
        ])
