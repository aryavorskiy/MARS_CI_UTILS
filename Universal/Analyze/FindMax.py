from Universal.ParseUtils import print_progressbar


def push_to_top(top_data, element, compare):
    """
    Helper method of get_top. Pushes an element to top in respect with order.

    :param top_data: List of pairs, each containing an object and number of times it was met in the list
    :param element: Object to add to the top
    :param compare: Lambda used to compare objects. See get_top documentation for more info
    :return: None
    """
    if element in [record[0] for record in top_data]:
        index = [record[0] for record in top_data].index(element)
        top_data[index][1] += 1
    else:
        insert_index = 0
        while insert_index < len(top_data) and compare(top_data[insert_index][0], element):
            insert_index += 1
        top_data.insert(insert_index, [element, 1])


def get_top(data, top_length, compare=lambda x, y: x > y, verbose=True):
    """
    Gets top objects by some qualifier.

    :param data: Some collection with objects to create top
    :param top_length: Number of elements to be in the top
    :param compare: Lambda used to compare objects. Result compare(top, x) will be true for any x,
    considered (compare(x, y) and compare(y, x)) => compare(x, z)
    :param verbose: Show progressbar if true
    :return: List of pairs. Each pair contains an object and number of times it was met in the list
    """
    top_data = []
    for i in range(len(data)):
        push_to_top(top_data, data[i], compare)
        if verbose:
            print_progressbar(i, len(data), prefix='Selecting best objects for top...')
        if len(top_data) > top_length:
            top_data.pop()
    return top_data


def verbose_top(top_data, filename=None):
    """
    Prints the top data in a beautiful way.

    :param top_data: List with (object, count) pairs produced by get_top()
    :param filename: Filename to write top data to. Set to None to write to stdout
    :return: None
    """
    writer = None if filename is None else open(filename, 'w')
    for top_record in top_data:
        line = '#{:>3}: {:<10} with {:^5} hits'.format(top_data.index(top_record) + 1, *top_record)
        if str(top_record[0]).count('\n') != 0:
            line += '\n'
        print(line, file=writer)


def analyze_set_top(data, top_length):
    """
    Prints top first and last objects from a list.
    Objects should be comparable!

    :param data: Collection of objects to obtain top from
    :param top_length: Number of elements to be in top
    :return:
    """
    print('Top-{} items:'.format(top_length))
    verbose_top(get_top(data, top_length))
    print('Bottom-{} items:'.format(top_length))
    verbose_top(get_top(data, top_length, compare=lambda x, y: x < y))
