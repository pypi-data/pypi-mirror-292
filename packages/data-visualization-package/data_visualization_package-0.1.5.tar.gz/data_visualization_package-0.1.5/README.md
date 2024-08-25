# Data Visualization Package

A Python package for data visualization, including interactive and custom graphs.

## Features

- Creation of line, bar and scatter graphs.
- Interactive view with zoom and pan support.
- Export of graphics to PNG, SVG, and PDF formats.

## Installation

You can install the package directly from GitHub or PyPI:

```bash
pip install git+https://github.com/gvicencotti/data_visualization_package.git
```

## Data Visualization Package Usage

Here’s a basic example of how to use the package:

from data_visualization_package.data_loader import load_csv
from data_visualization_package.plotter import plot_line

# Load data from a CSV file
df = load_csv('path/to/your_data.csv')

# Create a line plot
plot_line(df, 'x_column', 'y_column')

Parameters
file_path: The path to the CSV file you want to load.
dataframe: The DataFrame containing your data.
x_column: The name of the column to be used for the x-axis.
y_column: The name of the column to be used for the y-axis.

Supported Graphs
Line Graphs
Bar Graphs
Scatter Graphs

## Data Visualization Package

To ensure the package is working correctly, you can run the tests included in the repository. Here’s how to do it:

Install the Required Dependencies:

Make sure you have pytest installed. If not, you can install it using:

```bash
pip install pytest
```
Run the Tests:

```bash
python -m pytest tests/
```

## Credits

This project was developed with the help of OpenAI's ChatGPT, which contributed to defining the scope and provided implementation suggestions. Using AI tools like ChatGPT helped streamline the development process and refine the package's functionality.

## License

[MIT](https://choosealicense.com/licenses/mit/)
