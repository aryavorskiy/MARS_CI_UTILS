import numpy as np

from Universal.ParseExtensions import delimited_reader, print_progressbar


class NpArray:
    """
    Custom realization of NumPy array. Compare method overridden to make comparison of complex objects available.
    Added the append() method to achieve more compatibility.
    """

    def __init__(self, *args, **kwargs):
        self.__np_arr = np.array(*args, **kwargs)

    def append(self, element):
        """
        Appends an element to the array.
        Slow method, avoid intense usage.

        :param element: Element to add
        :return: None
        """
        self.__np_arr = np.append(self.__np_arr, element)

    def __getitem__(self, item):
        return self.__np_arr[item]

    def __setitem__(self, key, value):
        self.__np_arr[key] = value

    def __len__(self):
        return len(self.__np_arr)

    def __str__(self):
        return ' '.join(str(s) for s in self.__np_arr)

    def __mul__(self, other):
        output = NpArray(self)
        for i in range(len(output)):
            output[i] *= other
        return output

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __repr__(self):
        return 'MyArray({})'.format(repr(list(self.__np_arr)))


class Mat:
    """
    Represents a lattice struct.
    """

    def __init__(self, size=0):
        self.size = size
        self.mat = []

    def load(self, file: str, verbose=True):
        """
        Loads lattice values from given file.

        :param file: Name of file to read values from
        :param verbose: Show progressbar if true
        :return: None
        """
        reader = delimited_reader(open(file), ' ')
        self.size = int(reader.__next__())
        self.mat = []
        for word in reader:
            if verbose:
                print_progressbar(len(self.mat), self.size ** 2, prefix='Loading lattice...')
            self.mat.append(float(word))
            if len(self.mat) == self.size ** 2:
                break
        for i in range(self.size):
            for j in range(i):
                self[i, j] = self[j, i]
        for i in range(self.size):
            self[i, i] = 0

    def hamiltonian(self, spins: iter):
        """
        Calculates hamiltonian of given spin configuration.
        :param spins: Spin values
        :return: Float value representing hamiltonian
        """
        if len(spins) != self.size:
            raise ValueError('Spin count ({}) does not correspond to mat size ({})'.format(len(spins), self.size))
        hamiltonian = 0.
        for i in range(self.size):
            for j in range(i + 1, self.size):
                hamiltonian += self[i, j] * spins[i] * spins[j]
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
                return False
        return True

    def __getitem__(self, item):
        """
        Gets lattice element by given indices.
        :param item: Tuple with indices
        :return: Float value representing specified lattice element
        """
        return self.mat[item[0] * self.size + item[1]]

    def __setitem__(self, idx, value):
        """
        Sets lattice element by given indices to a specified value.
        :param idx: Tuple with indices
        :param value: Value to set
        :return: None
        """
        self.mat[idx[0] * self.size + idx[1]] = value


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
        Add new set to block
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
        :return: True if objects are considered equal, false otherwise
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

    def __str__(self):
        """
        :return: String representation of set info
        """
        return ''.join([f'Hamiltonian: {self.hamiltonian}, ',
                        f'{self.steps} annealing steps, ' if self.steps is not None else '',
                        f'type: {self.set_type}, ' if self.set_type is not None else 'type: Undefined, ',
                        f'spins:\n{self.spins}\nInitial spins:\n{self.initial_spins}\n' if self.spins is not None
                        else ''
                        ])
