import math
from math import log10


def get_histogram(data, start, end, count, mode='center'):
    """
    This function creates a histogram from given data.

    :param data: List of numbers to create a histogram from
    :param start: Left bound of the histogram
    :param end: Right bound of the histogram
    :param count: Quantity of histogram intervals
    :param mode: Type of curve to return; 'center', 'left' or 'curve' possible
    :return: Tuple of two lists with x- and y-coordinates of points respectively
    """
    step = (end - start) / count
    histogram_points = [[(start + step * i, start + step * (i + 1)), 0] for i in range(count)]
    for point in data:
        interval_no = math.floor((point - start) / step)
        if 0 <= interval_no < count:
            histogram_points[interval_no][1] += 1
    x_coords = []
    y_coords = []
    for final_point in histogram_points:
        prob_density = 0 if len(data) == 0 else final_point[1] / (step * len(data))
        if mode == 'curve':
            x_coords.extend(final_point[0])
            y_coords.extend((prob_density,) * 2)
        elif mode == 'center':
            x_coords.append(sum(final_point[0]) / 2)
            y_coords.append(prob_density)
        elif mode == 'left':
            x_coords.append(final_point[0][0])
            y_coords.append(prob_density)

    return x_coords, y_coords


def get_bounds(data):
    """
    Automatically chooses histogram bounds for a given data set.

    :param data: List of numbers to choose bounds for
    :returns: Tuple of two numbers representing bounds
    """
    upper_bound = max(data)
    lower_bound = min(data)
    step = 0.5 * 10 ** int(log10(abs(upper_bound - lower_bound)))
    return step * int(lower_bound // step - 1), step * int(upper_bound // step + 1)
