import numpy as np

from Modules.ParseExtensions import delimited_reader, print_progressbar


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
            if verbose and len(self.mat) % 100 == 0:
                print_progressbar(len(self.mat), self.size ** 2, prefix='Loading lattice...')
            self.mat.append(float(word))
            if len(self.mat) == self.size ** 2:
                break
        for i in range(self.size):
            for j in range(i):
                self[i, j] = self[j, i]
        for i in range(self.size):
            self[i, i] = 0
        if verbose:
            print()

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
                if verbose:
                    print()
                return False
        if verbose:
            print()
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


class SetInfo:
    """
    Represents a set of spins struct. Two sets considered equal if resulting spin values match.
    """

    def __init__(self, start_temperature, spins, hamiltonian, steps, set_type='Undefined', initial_spins=None):
        """
        :param start_temperature: Start temperature
        :param spins: Resulting spin values collection
        :param hamiltonian: Resulting hamiltonian
        :param steps: Number of annealing steps required to achieve the result
        :param set_type: Set type - Independent, No-anneal, Dependent or Undefined
        :param initial_spins:
        """
        self.start_temperature = float(start_temperature)
        self.spins = spins if type(spins) == NpArray else NpArray(spins)
        self.hamiltonian = float(hamiltonian)
        self.steps = steps
        self.set_type = set_type
        self.initial_spins = initial_spins if type(initial_spins) == NpArray or initial_spins is None \
            else NpArray(initial_spins)

    def __eq__(self, other):
        """
        Compare two SetInfo objects.

        :param other: The other SetInfo object to compare with
        :return: True if objects are considered equal, false otherwise
        """
        if type(self) != type(other):
            raise TypeError('Type mismatch: unable to compare {} with {}'.format(
                type(self), type(other)))
        return self.hamiltonian == other.hamiltonian and (self.spins == other.spins or self.spins == other.spins * -1)

    def __str__(self):
        """
        :return: String representation of set info
        """
        return 'Hamiltonian: {}, {} annealing steps, type: {}, spins:\n{}\ninitial spins:\n{}\n'.format(
            self.hamiltonian, self.steps, self.set_type, self.spins, self.initial_spins)
