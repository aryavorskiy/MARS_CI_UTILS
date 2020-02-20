import matplotlib.pyplot as plt


class Plot:
    """
    Simple MatPlotLib wrapper class.
    """

    def __init__(self, title, title_x='', title_y=''):
        self.title = title
        self.title_x = title_x
        self.title_y = title_y
        self.plot_data = []

    def add_plot_data(self, curve, shape='r^', legend=''):
        """
        Adds curve to plot data.
        :param curve: Tuple of two lists with x- and y-coordinates of points respectively
        :param shape: Shape description as in MatPlotLib
        :param legend: Text label to show in the plot legend
        :return: None
        """
        self.plot_data.append((*curve, shape, legend))

    def delete_plot_data(self):
        """
        Delete all plot data.
        :return: None
        """
        self.plot_data.clear()

    def plot_all(self):
        """
        Plot all data that was previously loaded.
        :return: None
        """
        plt.figure(figsize=(16, 12))
        plt.title(self.title)
        plt.xlabel(self.title_x)
        plt.ylabel(self.title_y)
        plt.grid(axis='both')
        for data in self.plot_data:
            plt.plot(*data[:-1], label=data[-1])
        plt.legend()
        plt.show()
