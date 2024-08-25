import pandas as pd
from plotter import plot_line, plot_bar, plot_scatter_interactive

dataframe = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [10, 15, 7, 10]})

def test_plot_line():
    plot_line(dataframe, 'x', 'y', title='Line Graph Test')

def test_plot_bar():
    plot_bar(dataframe, 'x', 'y', title='Bar Graph Test')

def test_plot_scatter_interactive():
    plot_scatter_interactive(dataframe, 'x', 'y', title='Interactive Scatter Plot Test')