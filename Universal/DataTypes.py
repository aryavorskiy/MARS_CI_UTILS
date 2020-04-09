import numpy as np


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
