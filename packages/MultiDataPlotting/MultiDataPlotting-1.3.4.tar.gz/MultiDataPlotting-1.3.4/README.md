# MultiDataPlotting

`MultiDataPlotting` is a Python package designed for easy and efficient plotting of multiple data sets, providing tools for generating bar plots, scatter plots, and other types of visual data representations. It leverages popular libraries such as Matplotlib, Seaborn, and Pandas to offer a versatile set of plotting functionalities.

## Features

- Plot multiple data sets in a single figure.
- Support for various types of plots: bar plots, scatter plots, line plots, rose maps.
- Customizable plot settings: colors, labels, legends, and more.
- Integration with Pandas for direct data frame plotting.

## Installation

You can install `MultiDataPlotting` using pip:

```bash
pip install MultiDataPlotting
```

## Usage

To use the package, you can import it into your Python scripts as follows:

```python
import multidataprocessing as mdp
```

### Plotting Beeswarm with Reference Lines

The `plot_beeswarm` function in our advanced data visualization toolkit offers a comprehensive method for displaying beeswarm plots that highlight medians and interquartile ranges (IQRs), along with optional horizontal reference lines for key values such as optimizer or desired outcomes. This function is ideal for statistical analysis across various categories or conditions in fields like environmental science, economics, and health sciences.

_Functionality_

This function facilitates the visualization of value distributions across different categories with additional context provided by horizontal reference lines, which can be set according to the user's specific needs (e.g., target values, thresholds). It helps in understanding data spread, central tendency, and compliance with desired or optimal values.

_Parameters_
- **categories** (list): Category labels for the x-axis.
- **values** (list of arrays): Data points for each category.
- **optimizer_value** (float, optional): The optimizer value to plot as a horizontal dashed line. Default is `None`.
- **desired_value** (float, optional): The desired target value to plot as a horizontal solid line. Default is `None`.
- **fig_size** (tuple, optional): Dimensions of the figure in inches. Default is `(12, 8)`.
- **swarm_color** (str, optional): Color of the swarm points. Default is 'gray'.
- **swarm_size** (int, optional): Size of the swarm points. Default is 2.
- **swarm_transparency** (float, optional): Transparency of swarm points. Default is `None`.
- **median_color** (str, optional): Color of the median points. Default is 'black'.
- **median_edge_color** (str, optional): Edge color of the median points. Default is 'none'.
- **median_size** (int, optional): Size of the median points. Default is 30.
- **line_color** (str, optional): Color of the IQR lines and desired value line. Default is 'black'.
- **line_thickness** (int, optional): Thickness of the IQR and desired value lines. Default is 2.
- **optimizer_color** (str, optional): Color of the optimizer line. Default is 'black'.
- **optimizer_style** (str, optional): Style of the optimizer line. Default is '--'.
- **optimizer_thickness** (int, optional): Thickness of the optimizer line. Default is 1.5.
- **desired_color** (str, optional): Color of the desired value line. Default is 'blue'.
- **desired_style** (str, optional): Style of the desired value line. Default is '-'.
- **desired_thickness** (int, optional): Thickness of the desired value line. Default is 1.5.
- **title** (str, optional): Title of the plot. Default is 'Subcatchment Area Distribution by Site'.
- **xlabel_name** (str, optional): Label for the x-axis. Default is 'Category'.
- **ylabel_name** (str, optional): Label for the y-axis. Default is 'Subcatchment Area (km²)'.
- **xlabel_size** (int, optional): Font size for the x-axis label. Default is 12.
- **ylabel_size** (int, optional): Font size for the y-axis label. Default is 12.
- **xlabel_font** (str, optional): Font family for the x-axis label. Default is 'Arial'.
- **ylabel_font** (str, optional): Font family for the y-axis label. Default is 'Arial'.
- **tick_font_name** (str, optional): Font family for tick labels. Default is 'Arial'.
- **tick_font_size** (int, optional): Font size for tick labels. Default is 10.
- **xtick_rotation** (int, optional): Rotation angle of x-axis tick labels. Default is 0.
- **y_range** (tuple, optional): Y-axis range for the plot. Default is `None`.
- **is_show** (bool, optional): Whether to display the plot on screen. Default is True.
- **save_path** (str, optional): File path to save the plot image, if desired.

_Code Example_

```python
import numpy as np
import pandas as pd
import multidataplotting as mdp

categories = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']  # Example categories
values = [np.random.rand(150) * 1.0 + 0.5 for _ in categories]  # Random data generation for illustration
optimizer_value = 1.2  # Example value for optimizer bandwidth
desired_value = 1.0  # Example value for desired value

mdp.plot_beeswarm(categories, values, optimizer_value = optimizer_value , desired_value=desired_value)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/beeswarm.png?raw=true)

### Plotting Clustered Data with Boundaries
The `plot_clustered_data` function in the advanced data visualization toolkit allows for the visual representation of data clusters from a pandas DataFrame. This function is highly versatile, supporting multiple clustering methods and customizable plot aesthetics, including the option to draw smoothed boundaries around clusters. It is particularly useful in fields such as market segmentation, bioinformatics, environmental analysis, and any other area where data clustering provides insight.

_Functionality_

This function provides a detailed clustering and visualization of multidimensional data. Users can select specific columns for clustering and choose different axes for visualization. It supports various clustering algorithms, and it can visually delineate cluster boundaries, enhancing the interpretability of cluster separation and density. This makes it an invaluable tool for comprehensive data analysis and presentation.

_Parameters_
- **df** (pandas.DataFrame): The DataFrame containing the data.
- **columns** (list): Column indices or names to include in the clustering.
- **x_index** (int or str): Column index or name for the x-axis of the plot.
- **y_index** (int or str): Column index or name for the y-axis of the plot.
- **n_clusters** (int, optional): Number of clusters for certain algorithms. Default is 3.
- **method** (str, optional): Clustering method; options include 'KMeans', 'Agglomerative', 'DBSCAN', 'Spectral', or 'GaussianMixture'. Default is 'KMeans'.
- **marker_size** (int, optional): Size of the markers in the plot. Default is 50.
- **marker_colors** (list or dict, optional): Colors for the markers, specified as a list or dictionary mapping clusters to colors. Defaults to the 'viridis' colormap.
- **marker_type** (str, optional): Shape of the markers, such as 'o' (circle), 'x' (cross). Default is 'o'.
- **fig_size** (tuple, optional): Dimensions of the figure in inches. Default is (10, 5).
- **tick_font_size** (int, optional): Font size for tick labels. Default is 12.
- **tick_font_name** (str, optional): Font family for tick labels. Default is 'Arial'.
- **xlabel** (str, optional): Label for the x-axis. Default is 'X-axis'.
- **ylabel** (str, optional): Label for the y-axis. Default is 'Y-axis'.
- **label_font_size** (int, optional): Font size for axis labels. Default is 14.
- **is_legend** (bool, optional): Whether to display a legend for the clusters. Default is True.
- **cluster_names** (list, optional): Custom names for each cluster in the legend. Defaults to generic names like "Cluster 0".
- **is_show** (bool, optional): Whether to display the plot on screen. Default is True.
- **save_path** (str, optional): File path to save the plot image, if desired.
- **is_boundary** (bool, optional): Whether to draw smooth boundaries around each cluster using a convex hull. Default is False.
- **boundary_color** (str, optional): Color of the boundary lines. Default is 'black'.
- **boundary_linewidth** (int, optional): Width of the boundary lines. Default is 2.
- **boundary_alpha** (float, optional): Transparency of the boundary lines. Default is 0.5.

_Code Example_

```python
import pandas as pd
import numpy as np
import multidataplotting as mdp
np.random.seed(4444)  # For reproducible results
data = {
    'Feature1': np.random.normal(loc=0, scale=1, size=100),  # Normal distribution centered at 0
    'Feature2': np.random.normal(loc=5, scale=2, size=100),  # Normal distribution centered at 5
    'Feature3': np.random.normal(loc=10, scale=3, size=100)  # Normal distribution centered at 10
}

# Create DataFrame
df = pd.DataFrame(data)
# Example usage:
# Assuming 'df' is your DataFrame and it contains columns that you want to cluster
mdp.plot_clustered_data(df, ['Feature1', 'Feature2', 'Feature3'], 'Feature1', 'Feature2',
                    method='KMeans', marker_type='^', cluster_names=['Type A', 'Type B', 'Type C'], is_legend=True, is_boundary=True)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/clusters.png?raw=true)

### Heatmap Plotting on Geographic Maps

The `plot_heatmap_on_geomap` function facilitates the visualization of spatial data distributions by rendering heatmaps on geographic maps. It supports two mapping backends, Basemap and OpenStreetMap (OSM), offering flexibility in the appearance and detail of the underlying geographic context. This function is ideal for environmental studies, meteorology, urban planning, and other disciplines requiring geographic data visualization.

_Functionality_

This function overlays heatmap data onto a geographic map, allowing for precise visualization adjustments. It supports various customization options, including transparency thresholds, colormap choices, and tick formatting. The integration of Basemap and OpenStreetMap ensures broad applicability for different visualization needs.

_Parameters_

- **data** (numpy.ndarray): The 2D array of data points to be visualized as a heatmap.
- **top_left_lat, top_left_lon** (float): The latitude and longitude of the top-left corner of the map.
- **bottom_right_lat, bottom_right_lon** (float): The latitude and longitude of the bottom-right corner of the map.
- **threshold** (float): The data value threshold below which points will be transparent.
- **cmap** (str, optional): Colormap for the heatmap. Default is 'jet'.
- **map_choice** (str, optional): Backend map provider ('base' for Basemap, 'osm' for OpenStreetMap). Default is 'base'.
- **zoom** (int, optional): Zoom level for the map when using OSM. Default is 10.
- **is_show** (bool, optional): Whether to display the plot. Default is True.
- **save_path** (str, optional): Path to save the figure. If not specified, the figure is not saved.
- **title** (str, optional): Title of the plot. Default is 'Heatmap Overlay on Geomap'.
- **colorbar_label** (str, optional): Label for the colorbar. Default is 'Data Intensity'.
- **fig_size** (tuple, optional): Figure dimensions in inches. Default is (8, 6).
- **x_tick_interval, y_tick_interval** (float, optional): Interval between ticks on the x and y axes.
- **tick_format** (str, optional): Format string for tick labels. Default is "{:.2f}".

_Code Example_

```python
import numpy as np
import multidataplotting as mdp

data = np.random.rand(100, 100)
mdp.plot_heatmap_on_geomap(data, 48.0, -123.0, 45.0, -120.0, threshold=0.75, map_choice='osm', x_tick_interval=1, y_tick_interval=1, tick_format="{:.2f}")

```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/heatgeomap.png?raw=true)


### Plotting Data by Quadrants

The `plot_quadrant_data` function in our toolkit provides a robust method for displaying data points categorized by defined thresholds on both the x and y axes. This function is ideal for applications in fields such as finance, meteorology, and health sciences where data is often analyzed by its position relative to critical thresholds.

_Functionality_

This function categorizes and visualizes data points into quadrants based on user-specified x and y threshold values. It supports customization of various plot aspects including category names, marker aesthetics, and plot labels, enhancing the interpretability and visual appeal of the output.

_Parameters_
- **data** (pandas.DataFrame): The DataFrame must contain 'x' and 'y' columns.
- **x_threshold** (float): Threshold value for categorizing data along the x-axis.
- **y_threshold** (float): Threshold value for categorizing data along the y-axis.
- **fig_size** (tuple): Figure size; default is (10, 8)
- **category_names** (list, optional): Custom names for each category; default categories are 'Above Left', 'Above Right', 'Below Left', 'Below Right', 'On Line'.
- **xlabel** (str, optional): Label for the x-axis. Default is 'Centroid offset (mm)'.
- **ylabel** (str, optional): Label for the y-axis. Default is 'Edge height difference (mm)'.
- **title** (str, optional): Title of the plot. Default is 'Classification of Data Relative to Threshold Lines'.
- **xlabel_size**, **ylabel_size**, **title_size** (int, optional): Font sizes for the x-axis label, y-axis label, and title.
- **marker_color** (str or list, optional): Color map or list of colors for the markers. Default is 'viridis'.
- **marker_size** (int, optional): Size of the markers. Default is 100.
- **x_tick_interval**, **y_tick_interval** (float, optional): Custom intervals for x and y axis ticks.
- **tick_font** (str, optional): Font family for tick labels. Default is 'Arial'.
- **tick_font_size** (int, optional): Font size for tick labels. Default is 10.
- **is_show** (bool, optional): If True, display the plot on screen. Default is True.
- **is_legend** (bool, optional): If True, display a legend for the categories. Default is True.
- **save_path** (str, optional): File path to save the plot image, if desired.

_Code Example_

```python
import pandas as pd
import numpy as np
import multidataplotting as mdp

# Example data
np.random.seed(0)
data = pd.DataFrame({
    'x': np.random.normal(0, 50, 300),
    'y': np.random.normal(0, 5, 300)
})

# Define thresholds
x_threshold = 0  # Example threshold for x-axis
y_threshold = 0  # Example threshold for y-axis

# Classify the data
mdp.plot_quadrant_data(data, x_threshold, y_threshold)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/quadrant.png?raw=true)

### Plotting Grouped Dot Chart with Vertical Lines

The `plot_grouped_dot_chart` function in our data visualization toolkit provides a dynamic method for creating grouped dot charts with vertical connecting lines to the x-axis. This function is particularly useful for visualizing categorical data comparisons across different states or groups, highlighting individual data points and their distribution within each category.

_Functionality_

This function enables the visualization of numerical data across categorical groups with enhancements that visually connect each data point to the baseline, thereby facilitating a clearer understanding of value distribution and differences between groups.

_Parameters_
- **data** (DataFrame): The DataFrame containing the data to be plotted. Must include categorical and numerical columns.
- **category_col** (str): The column name in DataFrame used as the categorical axis (e.g., 'State').
- **value_cols** (list of str, optional): The column names to be plotted as numerical values. If `None`, all columns except `category_col` are used.
- **label_size** (int, optional): Font size for the axis labels. Default is 12.
- **tick_label_size** (int, optional): Font size for the tick labels. Default is 10.
- **cmap** (str, optional): Name of the matplotlib colormap used for differentiating categories. Default is 'tab20'.
- **font_name** (str, optional): Font family for text elements in the plot. Default is 'Arial'.
- **is_legend** (bool, optional): Whether to display the legend in the plot. Default is True.
- **is_show** (bool, optional): Whether to display the plot on screen after drawing. Default is True.
- **fig_size** (tuple, optional): Dimensions of the figure in inches. Default is (10, 8).
- **save_path** (str, optional): File path to save the plot image, if desired. Default is None.

_Code Example_

```python
import pandas as pd
import multidataplotting as mdp

# Example data
data = pd.DataFrame({
    'State': ['CA', 'TX', 'NY', 'FL', 'IL', 'PA'],
    'Under 5 Years': [2.5, 3.0, 1.5, 2.0, 1.8, 2.1],
    '5 to 13 Years': [4.0, 4.5, 2.5, 3.5, 3.0, 3.6],
    '14 to 17 Years': [1.0, 1.2, 0.8, 1.1, 1.0, 0.9],
    '18 to 24 Years': [2.8, 3.2, 1.9, 2.5, 2.2, 2.8],
    '25 to 44 Years': [8.0, 7.5, 4.5, 6.0, 5.5, 5.9],
    '45 to 64 Years': [7.5, 8.0, 5.0, 6.5, 6.0, 6.4],
    '65 Years and Over': [5.0, 5.5, 3.5, 4.0, 3.8, 4.2]
})
mdp.plot_grouped_dot_chart(data, is_legend=True, is_show=True, fig_size=(12, 8))

```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/dotline.png?raw=true)

### Plot Ridgelines

The `plot_ridgelines` function is a specialized visualization tool designed for creating impactful ridgeline plots, which are ideal for displaying the distribution of data across different categories, such as time periods or groups. This function is versatile and can be tailored for various data analysis needs, especially useful in statistics, finance, environmental science, and more.

_Functionality_

This function generates ridgeline plots that help in visualizing changes or distributions over categories with a clear, artistic representation. The use of color gradients or monochrome palettes enhances the visual appeal and helps in distinguishing between categories effectively.

_Parameters_
- **data** (Dictionary or DataFrame): Contains the data for each category. If a dictionary, it will be converted into a DataFrame.
- **categories** (list): A list of categories representing each dataset, like months or groups.
- **x_label** (str): Label for the x-axis.
- **title** (str): Title of the plot.
- **cmap** (str, optional): Color palette to use. If None, a black and white scheme is employed.
- **tick_interval** (float, optional): Specifies the interval between ticks on the x-axis. If None, the default is used.
- **tick_size** (int): Font size for the x-axis ticks.
- **tick_font** (str): Font family for the x-axis ticks.
- **category_size** (int): Font size for category labels.
- **category_font** (str): Font family for category labels.
- **title_size** (int): Font size for the plot title.
- **save_path** (str, optional): If provided, the plot will be saved to the specified path.
- **is_show** (bool): If True, the plot will be displayed. If False, the plot will be closed after creation.
- **is_legend** (bool): If True, a legend mapping colors to categories will be displayed.
- **fig_size** (tuple): Dimensions of the figure (width, height).

_Code Example_

```python
import pandas as pd
import numpy as np
import multidataplotting as mdp
# Sample data creation
np.random.seed(10)
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
data = {month: np.random.normal(loc=20 + i, scale=5, size=100) for i, month in enumerate(months)}
# Example usage
mdp.plot_ridgelines(data, months, 'Mean Temperature [F]', 'Temperatures by Month', cmap='viridis', tick_interval=5)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/ridge.png?raw=true)

### Plotting Time Histograms

The `plot_time_histogram` function creates histograms based on time data, ideal for visualizing event frequencies over specific intervals. This method helps in identifying trends and patterns by illustrating how event occurrences are distributed across different time points.

_Functionality_

This function is particularly useful in scenarios such as analyzing user activity logs, sales data over time, or any periodic data that is timestamped. It helps in understanding the distribution and concentration of events, aiding in decision-making processes like resource allocation during peak times

_Parameters_

- **histogram** (dict): Dictionary with datetime keys (either strings or objects) and frequency counts as values.
- **color** (str, optional): Color of the histogram bars. Default is 'blue'.
- **edgecolor** (str, optional): Color of the bar edges. Default is 'black'.
- **fig_size** (tuple, optional): Size of the figure in inches. Default is (10, 6).
- **tick_fontname** (str, optional): Font name for the tick labels. Default is 'Arial'.
- **tick_fontsize** (int, optional): Font size for the tick labels. Default is 12.
- **title_fontsize** (int, optional): Font size for the title of the plot. Default is 14.
- **label_fontsize** (int, optional): Font size for the axis labels. Default is 14.
- **y_range** (list, optional): List specifying the y-axis limits as [min, max]. If not set, the axis scales automatically.
- **x_tick_interval_minutes**: (int,optional): the interval of the x ticks in minutes
- **x_ticklabel_format** (str, optional): Format of the x-tick labels, can be 'HH' for hours and minutes, or 'YYYY-MM-DD' for dates. Default is 'HH'.
- **is_legend** (bool, optional): Indicates whether to display a legend. Default is False.
- **save_path** (str, optional): File path where the plot will be saved, if desired. If not provided, the plot is not saved.
- **is_show** (bool, optional): Whether to display the plot on the screen. Default is False.
- **is_save** (bool, optional): Whether to save the plot to a file. Default is True.
- **transparent_bg** (bool, optional): Whether the background of the saved figure should be transparent. Default is True.

_Code Example_

```python
import multidataplotting as mdp

# Example histogram data
# Example usage with datetime conversion
login_data = {
    '00:00:00 - 00:03:00': 100,
    '00:03:00 - 00:06:00': 150,
    '00:07:00 - 00:12:00': 125,
    '00:19:00 - 00:23:00': 175,
    '00:29:00 - 00:33:00': 175,
}

mdp.plot_time_histogram(login_data, color='blue', edgecolor='black', is_show=True)
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/timehist.png?raw=true)

### Plotting Polylines

The `plot_polylines` function in the multidataprocessing package is designed to plot multiple lines from a DataFrame using specified columns for the x and y axes. This functionality is essential for visualizing trends and relationships in data over time or across categories.

_Functionality_

This function is invaluable for comparing trends across multiple datasets, enabling clear insights into how different variables evolve concurrently. It is particularly useful in financial analysis, environmental monitoring, or any scientific data visualization involving multiple variables.

_Parameters_

- **df** (pandas.DataFrame): The DataFrame containing the data to plot.
- **x** (int): Index of the column in the DataFrame to use as the x-axis.
- **ys** (list of int): Indices of columns to plot on the y-axis.
- **line_styles** (dict, optional): Dictionary specifying line styles for each y-column plotted, with keys as column indices and values as style strings. Default is solid lines for all.
- **line_widths** (dict, optional): Dictionary specifying line widths for each plotted y-column, with keys as column indices and values as numeric widths. Default is 2 for all lines.
- **line_colors** (dict, optional): Dictionary specifying colors for each plotted y-column, with keys as column indices and values as color names or hex codes. Default is 'blue' for all lines.
- **legends** (list, optional): List of legend labels corresponding to each y-column. If not provided, column names are used as labels.
- **marker_colors** (dict, optional): Dictionary specifying marker colors for each y-column, enhancing distinctiveness of each line.
- **fig_size** (tuple, optional): Size of the figure in inches. Default is (10, 6).
- **x_tick_interval** (int, optional): Interval at which x-axis ticks should be placed. Default is 1.
- **markers** (dict, optional): Dictionary specifying marker styles for each y-column plotted, adding visual distinction to the lines.
- **y_label** (str, optional): Label for the y-axis. If not provided, defaults to a generic label.
- **show_grid** (bool, optional): Whether to display a grid in the background of the plot. Default is True.
- **font_name** (str, optional): Font family for all text elements in the plot. Default is 'Arial'.
- **font_size** (int, optional): Font size for all text elements in the plot. Default is 12.
- **save_path** (str, optional): Path to save the figure to a file. If not specified, the figure is not saved.
- **dpi** (int, optional): Resolution of the saved figure in dots per inch. Default is 600.
- **y_range** (list, optional): Specific limits for the y-axis as [min, max].
- **is_show** (bool, optional): Whether to display the plot on the screen. Default is True.

_Code Example_

```python
import pandas as pd
import numpy as np
import multidataplotting as mdp

data = {
    'X': list(range(12)),
    'Product1': np.random.randint(1000, 5000, size=12),
    'Product2': np.random.randint(1000, 5000, size=12)
}

data = pd.DataFrame(data)
mdp.plot_polylines(data, x=0, ys=[1, 2], line_colors={1: 'red', 2: 'green'}, x_tick_interval = 2, markers={1: 'o', 2: 'x'})
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/polyline.png?raw=true)

### plot_rolling_series Function Documentation

The `plot_rolling_series` function is designed for visualizing time series data along with its rolling statistics such as rolling maximum, minimum, and average. This function allows for significant customization to suit various analytical and presentation needs.

_Functionality_

This function plots a given time series data with its rolling statistics to provide insights into trends, fluctuations, and overall behavior over a specified period. It includes options for visual customization and can be adapted for both simple exploratory analysis and detailed, polished presentations.

_Parameters_

- **data** (`pd.Series`): The time series data as a Pandas Series with a DateTime index.
- **rolling_period** (`int`): The number of periods to use for calculating rolling statistics.
- **title** (`str`): The title of the plot.
- **xlabel**, **ylabel** (`str`): Labels for the X and Y axes.
- **series_color**, **max_color**, **min_color**, **avg_color** (`str`): Colors for the original data series, rolling maximum, minimum, and average lines.
- **alpha** (`float`): Opacity for the original series plot, where 1 is opaque and 0 is transparent.
- **fig_size** (`tuple`): Dimensions of the figure (width, height).
- **line_width** (`int`): The thickness of the plotted lines.
- **line_style** (`str`): Style of the lines (e.g., '-', '--', '-.', ':').
- **legend_labels** (`dict`): Labels for the plot legend, should include keys for 'original', 'max', 'min', and 'avg'.
- **font_name** (`str`): Font family for all text elements in the plot.
- **font_size** (`int`): Font size for all text elements in the plot.
- **y_lim** (`tuple`): The limits for the Y-axis (min, max).
- **y_tick_interval**, **x_tick_interval** (`int`): Interval between ticks on the Y-axis and X-axis respectively.
- **is_grid** (`bool`): If True, displays a grid on the plot.
- **is_legend** (`bool`): If True, displays a legend on the plot.
- **is_label** (`bool`): If True, labels are displayed alongside lines.
- **save_path** (`str`, optional): Path to save the figure file.
- **is_show** (`bool`): If True, displays the plot.

_Code Example_

```python
import pandas as pd
import multidataplotting as mdp

dates = pd.date_range(start='2020-01-01', periods=1000)
data = pd.Series(np.random.randn(1000).cumsum(), index=dates)
legend_labels = {'original': 'Data', 'max': 'Max Roll', 'min': 'Min Roll', 'avg': 'Average Roll'}
mdp.plot_rolling_series(data, rolling_period=10, legend_labels=legend_labels, x_tick_interval=90, y_tick_interval=3, is_grid=False, font_name='Times New Roman', font_size=14, is_label=True)

```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/rolling.png?raw=true)

### Two-Colored Time Series Plot

The `plot_two_colored_time_series` function in our data visualization toolkit offers a distinctive way to visualize time series data by changing the color of the plot line based on a specified threshold value. This is particularly useful for highlighting segments of the data that exceed or fall below critical levels, such as temperature thresholds, stock price targets, or performance benchmarks.

_Functionality_

This function plots a time series where the line color changes above and below a predefined threshold. It intelligently divides segments that cross the threshold, ensuring that the transition between colors accurately represents the point at which the data crosses this boundary.

_Parameters_
- **data** (pandas Series): A pandas Series with a DateTime index and one column of values to plot.
- **threshold** (float): The value at which the plot line color changes.
- **title** (str): Title of the plot.
- **xlabel**, **ylabel** (str): Labels for the x-axis and y-axis.
- **color_above**, **color_below** (str): Colors for the line segments above and below the threshold, respectively.
- **line_style** (str): Style of the plot line (e.g., '-', '--', '-.', ':').
- **line_width** (float): Width of the plot line.
- **threshold_color** (str): Color of the threshold line.
- **threshold_style** (str): Style of the threshold line (e.g., '-', '--').
- **threshold_width** (float): Thickness of the threshold line.
- **fig_size** (tuple): Dimensions of the figure.
- **x_tick_interval**, **y_tick_interval** (float): Interval between ticks on the x-axis and y-axis.
- **tick_font_name**, **tick_font_size** (str, int): Font name and size for the tick labels.
- **is_legend** (bool): Whether to display the legend.
- **legend_text** (str): Text for the legend entries.
- **save_path** (str, optional): File path to save the plot image, if desired.
- **is_show** (bool, optional): Whether to display the plot. Defaults to True if not specified.

_Example Usage_
```python
import pandas as pd
import numpy as np
import multidataplotting as mdp
# Generating sample data
dates = pd.date_range(start="2021-01-01", periods=100)
values = np.random.normal(loc=52, scale=5, size=100)  # Generate random data
data = pd.Series(values, index=dates)
mdp.plot_two_colored_time_series(data, threshold=56, title="Temperature Over Time", xlabel="Time", ylabel="Temperature (°F)",
                             x_tick_interval=10, y_tick_interval=2, tick_font_name='Arial', tick_font_size=10,
                             color_above='red', color_below='black', line_style='-', line_width=1.5,
                             threshold_color='gray', threshold_style=':', threshold_width=3)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/two_color.png?raw=true)

### Scatter Plot with Threshold

The `plot_scatter_with_threshold` function in our visualization library creates a scatter plot where points are colored differently based on their position relative to a specified threshold value. This function is ideal for highlighting distributions and differences in datasets relative to a critical value.

_Functionality_

This function generates a scatter plot with two distinct color mappings for data points lying above and below a given threshold. The saturation of colors indicates the distance from the threshold, providing a clear visual representation of how data points deviate from a critical value. Additionally, a threshold line is drawn to visually segregate the data, enhancing the interpretability of the plot.

_Parameters_
- **data** (pandas DataFrame): Contains the data with 'x' and 'y' columns to be plotted.
- **threshold** (float): The critical value against which data points are evaluated and colored.
- **title** (str): The title of the plot.
- **xlabel**, **ylabel** (str): Labels for the x-axis and y-axis.
- **edge_color** (str, optional): Color of the edges of scatter plot markers.
- **base_color_above**, **base_color_below** (str): Color maps for points above and below the threshold.
- **fig_size** (tuple): The dimensions of the figure.
- **is_legend** (bool): Whether to display the legend.
- **legend_font_size** (int): Font size for the legend text.
- **legend_font_name** (str): Font family for the legend text.
- **line_color** (str): Color of the threshold line.
- **line_style** (str): Style of the threshold line (e.g., '-', '--').
- **line_thickness** (float): Thickness of the threshold line.
- **label_font_size** (int): Font size for the axis labels.
- **label_font_name** (str): Font family for the axis labels.
- **save_path** (str, optional): Path to save the plot image, if desired.
- **is_show** (bool, optional): Set to True to display the plot. Defaults to True if not specified.

_Example Usage_
```python
import pandas as pd
import numpy as np
import multidataplotting as mdp

# Example usage
df = pd.DataFrame({
    'x': np.random.rand(100),
    'y': np.random.randn(100)  # Simulated values centered around zero
})
mdp.plot_scatter_with_threshold(df, threshold=0, title="Scatter Plot Example", xlabel="Random X", ylabel="Random Y",
                            base_color_above='Blues', base_color_below='Reds')

```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/thresh_scatter.png?raw=true)

### Plotting Histograms

The `plot_histograms` function from the multidataprocessing package allows users to plot multiple histograms in a single figure. This feature is particularly useful for comparing the distributions of several datasets simultaneously, providing insights into variability, skewness, or similarity among the datasets.

_Functionality_

`plot_histograms` is ideal for statistical analysis and data exploration, helping to visualize and compare the frequency distributions of multiple groups or variables within the same graphical context. It's especially useful in fields like biostatistics, market research, and any area where distribution comparison is crucial.

_Parameters_

- **list_of_lists** (list of lists): A list where each sublist contains numeric data for one histogram.
- **titles** (list of str): Titles for each histogram. Must match the number of sublists in list_of_lists.
- **xlabels** (str or list of str, optional): X-axis labels for each histogram. Can be a single string or a list of strings matching the number of histograms.
- **ylabels** (str or list of str, optional): Y-axis labels for each histogram. Can be a single string or a list of strings matching the number of histograms.
- **bins** (int, optional): Number of bins for the histograms. Default is 10.
- **color** (str, optional): Color of the histogram bars. Default is 'blue'.
- **edgecolor** (str, optional): Color of the bar edges. Default is 'black'.
- **fig_size** (tuple, optional): Size of the figure, in inches. Default is (10, 6).
- **tick_fontname** (str, optional): Font name for the tick labels. Default is 'Arial'.
- **tick_fontsize** (int, optional): Font size for the tick labels. Default is 12.
- **title_fontsize** (int, optional): Font size for the titles of each plot. Default is 14.
- **label_fontsize** (int, optional): Font size for the labels. Default is 14.
- **value_range** (list, optional): Specific range of values to include in each histogram as [min, max].
- **line_color** (str, optional): Color of the mean line within each histogram. Default is 'red'.
- **show_all_xticklabels** (bool, optional): Whether to show all x-axis tick labels. Default is True.
- **line_style** (str, optional): Style of the mean line, such as '--' for dashed lines. Default is '--'.
- **line_width** (float, optional): Width of the mean line. Default is 2.
- **is_legend** (bool, optional): Whether to include a legend in the plots. Default is False.
- **unit** (str, optional): Unit of measurement for the data, useful for annotations. Default is 'm'.
- **is_log** (bool, optional): Whether to use a logarithmic scale for the y-axis. Default is False.
- **is_log_x** (bool, optional): Whether to use a logarithmic scale for the x-axis. Default is False.
- **is_fixed_y_range** (bool, optional): Whether to fix the y-axis range across all plots. Default is False.
- **y_range** (list, optional): Specific y-axis limits as [min, max] if is_fixed_y_range is True.
- **is_mean_value** (bool, optional): Whether to display the mean value on the histograms. Default is True.
- **is_scaled** (bool, optional): Whether to scale the data by a factor. Default is False.
- **scale_factor** (float, optional): Factor by which to scale the data if is_scaled is True. Default is 10.
- **save_path** (str, optional): File path where the plot will be saved, if desired.
- **is_show** (bool, optional): Whether to display the plot on the screen. Default is True.
- **is_save** (bool, optional): Whether to save the plot to a file. Default is True.
- **transparent_bg** (bool, optional): Whether the background of the saved figure should be transparent. Default is True.
- **hspace** (float, optional): Space between subplots, in normalized subplot coordinates. Default is 0.1.
- **label_sep** (str, optional): Separator for splitting the labels. Default is '_'.

_Code Example_

```python
import numpy as np
import multidataplotting as mdp

# Generate random age data for four groups
group1 = np.random.normal(loc=30, scale=5, size=100)  # Mean age 30, SD 5
group2 = np.random.normal(loc=40, scale=5, size=100)  # Mean age 40, SD 5
group3 = np.random.normal(loc=20, scale=5, size=100)  # Mean age 20, SD 5
group4 = np.random.normal(loc=50, scale=5, size=100)  # Mean age 50, SD 5
list_of_lists = [group1, group2, group3, group4]

# Titles for each histogram
titles = ["Group 1: 20s", "Group 2: 30s", "Group 3: 40s", "Group 4: 50s"]
xlabels = ['A', 'B', 'C', 'D']
ylabels = 'Frequency (%)'
# Plotting histograms
mdp.plot_histograms(list_of_lists, titles=titles, xlabels = None, ylabels = ylabels, is_show=True, hspace = 0.2, color = '#edf8b1')
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/hists.png?raw=true)

### Drawing Categorical Bar and Curve Plots

The `draw_cat_bar_curveplots` function from the multidataprocessing package combines categorical bar plots with overlaid curve plots. This feature allows for a detailed comparative analysis of primary data alongside secondary trends within the same visual context, making it ideal for simultaneous examination of discrete and continuous data aspects.

_Functionality_

This function is perfect for applications where understanding the relationship between categorical and continuous data is essential. It can be used in market research for product comparison across different time points, financial analysis showing categorical expenditure against revenue trends, or any scenario where integrated visualization provides deeper insights.

_Parameters_

- **main_result** (dict): Main categorical data to be plotted as bars. Keys should be categories and values the measurements.
- **other_data_list** (list of dicts): List of dictionaries for the curve plots, where each dictionary represents a dataset to be plotted as a curve over the bar plots.
- **bar_colors** (list, optional): List of colors for the bars in the bar plot. If not provided, a default set of colors is used.
- **bar_thickness** (float, optional): Thickness of the bars. Default is 0.8.
- **bar_edge_color** (str, optional): Color of the bar edges. Default is 'black'.
- **line_color** (str, optional): Color for all line plots. Default is 'black'.
- **cat_labels** (list, optional): the labels for each category
- **xlabels** (list, optional): the labels for the x-axis
- **ylabels** (list, optional): the labels for the y-axis
- **y_range** (list, optional): The range for the y-axis as [min, max]. If not set, the axis scales automatically.
- **fig_size** (tuple, optional): Size of the figure, in inches. Default is (10, 6).
- **line_thickness** (float or list, optional): Thickness of the lines for curve plots. Can be a single value or a list of values corresponding to each dataset.
- **tick_fontsize** (int, optional): Font size for the tick labels. Default is 10.
- **tick_fontname** (str, optional): Font name for the tick labels. Default is 'sans-serif'.
- **x_tick_interval** (int, optional): Interval between x-ticks, useful for densely packed x-axes. Default is 1.
- **is_show** (bool, optional): Whether to display the plot on the screen. Default is False.
- **is_save** (bool, optional): Whether to save the plot to a file. Default is True.
- **save_path** (str, optional): File path where the plot will be saved, if desired. If not specified, the plot is not saved.

_Code Example_

```python
import multidataplotting as mdp

# Main results for the bar plot
main_result = {'1993-01-01': [200, 10], '1993-01-03': [10, 240], '1993-01-05': [300, 100], '1993-01-06': [100, 120]}

# Additional data for curve plots
other_data_list = [
    {'1993-01-01': 150, '1993-01-02': 180, '1993-01-04': 210, '1993-01-07': 160},  # Product A
    {'1993-01-01': 100, '1993-01-03': 200, '1993-01-05': 230}   # Product B
]

# Plotting the combined bar and curve plots
mdp.draw_cat_bar_curveplots(
    main_result,
    other_data_list,
    bar_colors=['blue', 'green', 'red'],
    line_color='black',
    fig_size=(12, 8),
    tick_fontsize=12,
    is_show=True,
    cat_labels=['A', 'A+'],
    xlabels = ['', '', 'Date'],
    ylabels = ['Data 1', 'Data 2', 'Data 3']
)
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/cat_curve.png?raw=true)

### Plotting Bar Plots

The `plot_bar_plots` function from the multidataprocessing package is designed to plot multiple bar plots within a single figure, allowing for comparative analysis across different data sets or categories. This function is particularly useful for visualizing and comparing discrete data points across multiple groups or time intervals.

_Functionality_

This function is ideal for business reporting, scientific data comparison, or any scenario where multiple datasets need to be compared side-by-side. It enhances data presentation by providing clear, distinct visualizations that facilitate easy comparison of categorical data.

_Parameters_

- **list_of_lists** (list of lists): A list where each sublist contains data for one bar plot.
- **tuple_range_list** (list of tuples): A list of tuples specifying the range for each bar in the plots.
- **titles** (str or list of str, optional): Titles for each subplot. Can be a single string or a list of strings if there are multiple plots.
- **ylabels** (str or list of str, optional): Y-axis labels for each subplot. Can be a single string or a list of strings if there are multiple plots.
- **bar_color** (str, optional): Color of the bars in the plots. Default is 'blue'.
- **bar_edgecolor** (str, optional): Color of the bar edges. Default is 'black'.
- **fig_size** (tuple, optional): Dimensions of the entire figure, in inches. Default is (10, 6).
- **tick_fontname** (str, optional): Font name for the tick labels. Default is 'Arial'.
- **tick_fontsize** (int, optional): Font size for the tick labels. Default is 12.
- **title_fontsize** (int, optional): Font size for the titles of each subplot. Default is 14.
- **label_fontsize** (int, optional): Font size for the labels. Default is 14.
- **line_color** (str, optional): Color of the line indicating mean or median, if applicable. Default is 'red'.
- **show_all_xticklabels** (bool, optional): Whether to show all x-tick labels. Default is True.
- **bar_width** (float, optional): Width of the bars in the plots. Default is 1.
- **line_style** (str, optional): Style of the mean or median line, e.g., '--' for dashed. Default is '--'.
- **line_width** (float, optional): Width of the mean or median line. Default is 2.
- **is_legend** (bool, optional): Whether to show a legend in the plots. Default is False.
- **unit** (str, optional): Unit of measurement for the data, useful for annotations. Default is 'm'.
- **is_fixed_y_range** (bool, optional): Whether to fix the y-axis range across all plots. Default is True.
- **y_range** (list, optional): Specific y-axis limits as [min, max].
- **is_mean_value** (bool, optional): Whether to display the mean value on the histograms. Default is False.
- **is_scaled** (bool, optional): Whether to scale the data by a factor. Default is False.
- **scale_factor** (float, optional): Factor by which to scale the data, if is_scaled is True.
- **save_path** (str, optional): File path where the plot will be saved, if desired.
- **is_show** (bool, optional): Whether to display the plot on the screen. Default is False.
- **is_save** (bool, optional): Whether to save the plot to a file. Default is True.
- **transparent_bg** (bool, optional): Whether the background of the saved figure should be transparent. Default is True.
- **horizontal** (bool, optional): Whether the bars should be plotted horizontally. Default is False.
- **convert_minute** (bool, optional): Whether to convert the x-tick labels to minutes. Default is True.
- **hspace** (float, optional): The amount of height reserved for white space between subplots, expressed as a fraction of the average axis height. Default is 0.05.

_Code Example_

```python
import multidataplotting as mdp
import numpy as np

# Sample data
team_performance = [[20*np.random.random() for i in range(100)] for _ in range(3)]
range_tuples = [(1), (1, 3), (3,4), (4, 6), (6,7), (7, 9), (9, 12), (12, 15), (15, 18), (18)]  # Quarterly ranges

# Plotting the bar plots
mdp.plot_bar_plots(
    list_of_lists=team_performance,
    tuple_range_list=range_tuples,
    titles=["Team A", "Team B", "Team C"],
    ylabels="Score",
    bar_color='green',
    fig_size=(12, 8),
    is_scaled=False,
    is_show=True,
    convert_minute=False,
)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/barplot.png?raw=true)

### Plot Bins with Cumulative Distribution Function (CDF)

The `plot_bins_with_cdf` function provides a powerful way to visualize data distributions through a combined bar and line chart. This function is perfect for performing profit analysis across different categories, such as cities or outlets, and allows for an intuitive visual representation of both absolute and cumulative data.

_Functionality_

This function creates a dual-axis plot where one axis shows the raw data values (e.g., profits) as bars, and the other axis displays the cumulative distribution as a line chart with optional markers. The function supports both vertical and horizontal plot orientations, making it versatile for various reporting styles.

_Parameters_
- **data**: DataFrame or list of dictionaries containing the data. Each entry should have keys corresponding to the `cat_key_name` and `val_key_name`, and optionally `cum_key_name`.
- **cat_key_name**: The name of the column or key that contains categorical data (default 'city').
- **val_key_name**: The name of the column or key that contains value data (default 'profit').
- **cum_key_name**: The name of the column or key for pre-calculated cumulative data, if available (optional).
- **flip_axes**: Boolean flag to switch between vertical and horizontal plot orientations (default False).
- **bar_color**, **line_color**: Colors used for the bar and line plots, respectively.
- **marker_type**, **marker_face_color**, **marker_size**: Customizations for the markers in the line plot.
- **title**, **title_size**, **title_font**: Customizations for the plot's title.
- **xlabel**, **ylabel**, **label_font**, **label_size**: Labels for the x and y axes, and their styling.
- **tick_font**, **tick_size**: Font customizations for axis tick labels.
- **legend_loc**: Location of the legend on the plot.
- **fig_size**: The size of the figure to create.
- **is_legend**: Whether to display the legend (default True).
- **is_show**: Whether to display the plot after creation (default True).
- **save_path**: Optional path to save the plot image.

_Code Example_

```python
import pandas as pd
import numpy as np
import multidataplotting as mdp

# Example data
data = [
    {'city': 'Dallas', 'profit': 14400, 'cumulative': 15.44},
    {'city': 'Philadelphia', 'profit': 13600, 'cumulative': 30.02},
    {'city': 'Austin', 'profit': 13500, 'cumulative': 44.43},
    {'city': 'San Diego', 'profit': 11500, 'cumulative': 57.25},
    {'city': 'Chicago', 'profit': 9550, 'cumulative': 67.48},
    {'city': 'San Jose', 'profit': 7650, 'cumulative': 75.64},
    {'city': 'San Antonio', 'profit': 7130, 'cumulative': 82.26},
    {'city': 'Phoenix', 'profit': 7020, 'cumulative': 90.77},
    {'city': 'Los Angeles', 'profit': 4720, 'cumulative': 95.82},
    {'city': 'Houston', 'profit': 3950, 'cumulative': 100.00}
]

# Plotting
mdp.plot_bins_with_cdf(data, bar_color='#4daf4a', flip_axes=False)  # Change flip_axes to True for horizontal bars
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/bin_cdf.png?raw=true)

### Ternary Plot Visualization

The `plot_ternary` function in our data visualization toolkit is designed to create ternary diagrams, which are useful for displaying the proportions of three variables that sum to a constant. This tool is especially valuable in fields such as geochemistry, petrology, and materials science.

_Functionality_

This function generates a ternary diagram with customizable scaling, labels, and coloring. It supports dynamic adjustments to axis ticks, labels, and title settings, making it suitable for detailed scientific presentations and analyses.

_Parameters_

- **data** (list of tuples): Data to be plotted, where each tuple contains three proportions and a label (e.g., (A, B, C, 'Label')).
- **labels** (list of str): Labels for the three axes of the ternary plot.
- **scale** (int, optional): The scale for the ternary plot. Defaults to 100.
- **tick_interval** (int, optional): Interval for the tick marks on each axis. Defaults to 10.
- **color_map** (str, optional): Color map to use for differentiating data points. Defaults to 'viridis'.
- **title** (str, optional): Title of the plot. Defaults to "Spruce Composition Analysis".
- **title_font_size** (int, optional): Font size for the title. Defaults to 10.
- **fig_size** (tuple, optional): Size of the figure in inches. Defaults to (10, 8).
- **label_font_size** (int, optional): Font size for the axis labels. Defaults to 10.
- **label_offset** (float, optional): Offset for the axis labels. Defaults to 0.10.
- **tick_font_size** (int, optional): Font size for the tick labels. Defaults to 10.
- **tick_offset** (float, optional): Offset for the tick labels. Defaults to 0.01.
- **is_legend** (bool, optional): Whether to display a legend. Defaults to True.
- **is_show** (bool, optional): Whether to display the plot. Defaults to True.
- **save_path** (str, optional): Path to save the plot image, if specified.

_Code Example_

```python
import multidataplotting as mdp

example_data = [
    (0.1, 0.2, 0.7, 'Sitka'),
    (0.2, 0.7, 0.1, 'Engelmann'),
    (0.4, 0.5, 0.1, 'White'),
    (0.3, 0.3, 0.4, 'Sitka-White'),
    (0.2, 0.3, 0.5, 'Engelmann-White')
]
labels = ["Sitka Spruce", "Engelmann Spruce", "White Spruce"]

# Plot the ternary diagram with enhanced settings
mdp.plot_ternary(example_data, labels, color_map='viridis', tick_interval=10)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/triangle.png?raw=true)

### Plotting 2D Heatmaps

The `plot_2D_heatmap` function in the multidataprocessing package generates a two-dimensional heatmap from a dictionary of tuple pairs representing coordinate points and their respective frequency or intensity values. This visualization tool is especially useful for representing the density or intensity distribution across a two-dimensional space, making it applicable in areas like geographical data analysis, heat distribution, market density studies, and more.

_Functionality_

This function transforms raw data into a visually intuitive heatmap, allowing for the easy identification of patterns or concentrations within the data. It is invaluable for any analysis where understanding the spatial distribution of a variable is crucial.

_Parameters_

- **pair_freq** (dict): Dictionary with keys as tuple pairs of x and y coordinates (e.g., (x, y)) and values as their frequencies or intensities. Or a dataframe of two columns.
- **x_bin_ticks**(list, optional): a list of numbers, must locate within data range, if input is a dictionary, this is required, optional only if your input is a dataframe
- **y_bin_ticks**(list, optional): a list of numbers, must locate within data range, if input is a dictionary, this is required, optional only if your input is a dataframe
- **fig_size** (tuple, optional): The dimensions of the figure, in inches. Default is (10, 8).
- **title** (str, optional): The title of the heatmap. Default is 'Cross Relationship Heatmap'.
- **title_fontsize** (int, optional): Font size for the title. Default is 16.
- **xlabel** (str, optional): Label for the x-axis. Default is 'Variable 1'.
- **ylabel** (str, optional): Label for the y-axis. Default is 'Variable 2'.
- **label_fontsize** (int, optional): Font size for the axis labels. Default is 14.
- **tick_fontsize** (int, optional): Font size for the tick labels. Default is 12.
- **vmin** (float, optional): Minimum data value that corresponds to the colormap’s lower limit. If None, defaults to the data’s min value.
- **vmax** (float, optional): Maximum data value that corresponds to the colormap’s upper limit. If None, defaults to the data’s max value.
- **cmap** (str, optional): Colormap used for the heatmap. Default is 'viridis'.
- **cbar_label** (str, optional): Label for the colorbar. Default is 'Frequency'.
- **save_path** (str, optional): Path to save the figure. If provided, the plot is saved to this location.
- **is_show** (bool, optional): Whether to display the plot. Default is True.
- **xtick_rotation** (int, optional): Rotation angle for the x-axis tick labels. Default is 0.
- **ytick_rotation** (int, optional): Rotation angle for the y-axis tick labels. Default is 0.
- **xticklabels** (list, optional): Custom labels for the x-axis ticks. If None, default labels based on the data are used.
- **yticklabels** (list, optional): Custom labels for the y-axis ticks. If None, default labels based on the data are used.

_Code Example_

```python
import multidataplotting as mdp

# Example data: coordinates with frequencies
data = {
    (0, 0): 100, (0, 2): 70,
    (0, 1): 150, (1, 2): 205,
    (1, 0): 200, (2, 1): 160,
    (1, 1): 250, (2, 0): 95,
}
x_bin_ticks = [0, 1, 2]
y_bin_ticks = [0, 1, 2]
# Plotting the heatmap
mdp.plot_2D_heatmap(pair_freq=data, x_bin_ticks=x_bin_ticks, y_bin_ticks=y_bin_ticks,title="Event Frequency Distribution", 
                xlabel="X", ylabel="Y", is_show=True, is_annotate=True)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/heatmap.png?raw=true)


```python
import multidataplotting as mdp

# Example data: dataframe
data = [
    {'X': 1, 'Y': 1},
    {'X': 1, 'Y': 2},
    {'X': 2, 'Y': 1},
    {'X': 2, 'Y': 2},
    {'X': 2, 'Y': 4},
    {'X': 1.5, 'Y':1.8}
]
data = pd.DataFrame(data)
# Plotting the heatmap
plot_2D_heatmap(pair_freq=data, title="Event Frequency Distribution", 
                xlabel="X", ylabel="Y", is_show=True, is_annotate=True)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/heatmap2.png?raw=true)

### Contour Plot Visualization with Boundary and Condition Lines

The `plot_heatmap_with_bound_and_curves` function is an advanced visualization tool in our toolkit that creates detailed contour plots. It is specifically designed for performance analysis, where understanding the relationship between multiple variables within specified boundaries and under various conditions is crucial.

_Functionality_

This function generates a contour plot from a set of data points, applies a boundary to limit the area of interest, and overlays multiple condition lines with annotations. It is ideal for engine performance maps, environmental variable distributions, or any other application requiring a nuanced visualization of data within constraints.

_Parameters_

- **data** (DataFrame): Contains the 'x', 'y', and 'z' coordinates for generating the contour plot.
- **boundary_data** (DataFrame): Specifies the 'x' and 'y' points that define the boundary within which the data is visualized.
- **condition_lines** (list of DataFrames): Each DataFrame contains 'x' and 'y' coordinates for a condition line to be drawn on the plot.
- **condition_labels** (list of str): Labels for each condition line, placed near the end of each line.
- **fig_size** (tuple): Dimensions of the figure.
- **cmap** (str): Colormap for the contour plot.
- **colorbar_label** (str): Label for the color bar indicating what the colors represent.
- **boundary_color** (str), **boundary_linewidth** (int): Color and linewidth for the boundary.
- **line_styles**, **line_colors**, **line_widths** (lists): Styles, colors, and widths for each condition line.
- **title** (str), **title_size** (int): Title of the plot and its font size.
- **xlabel**, **ylabel** (str), **label_font_size** (int): Labels and font size for the x and y axes.
- **tick_font_size** (int): Font size for the tick labels on the axes.
- **is_legend** (bool): Whether to display a legend showing labels.
- **is_show** (bool): Whether to display the plot immediately.
- **save_path** (str, optional): Path where the plot image will be saved, if specified.

_Code Example_
```python
from scipy.interpolate import CubicSpline
import multidataplotting as mdp

# Generate sample engine data
engine_data = {
    'x': np.random.uniform(1000, 6000, 3000),
    'y': np.random.uniform(20, 150, 3000),
    'z': np.random.uniform(0, 1, 3000),  # Simulated performance data for demonstration
}

# Original boundary data points
original_boundary_data = {
    'x': np.array([1000, 1800, 2000, 2500, 4000, 4600, 6000]),
    'y': np.array([100, 120, 110, 100, 95, 120, 90])
}

# Create a smoother boundary using cubic spline interpolation
boundary_spline = CubicSpline(original_boundary_data['x'], original_boundary_data['y'], bc_type='natural')
xnew_boundary = np.linspace(1000, 6000, 300)  # More points for smoothness
ynew_boundary = boundary_spline(xnew_boundary)

# Update boundary data for smooth plotting
smooth_boundary_data = {
    'x': xnew_boundary,
    'y': ynew_boundary
}

smooth_boundary_data = {
    'x': xnew_boundary,
    'y': ynew_boundary
}

# Condition lines - polynomial fit for smoothness
smooth_condition_lines = []
condition_labels = ['100 HP', '75 HP']
hp_starts = [90, 70]

# Generating polynomial smoothed lines
for y_start in hp_starts:
    x_vals = np.linspace(1000, 6000, 100)
    # give a poly + ln format for yvals
    y_vals = y_start - 0.001 * x_vals ** 1.2 + 0.0001 * np.log(x_vals)
    smooth_condition_lines.append({'x': x_vals, 'y': y_vals})

mdp.plot_heatmap_with_bound_and_curves(
        data=engine_data,
        boundary_data=smooth_boundary_data,
        condition_lines=smooth_condition_lines,
        condition_labels=condition_labels,
        fig_size=(10, 7),
        title="Smooth Engine Performance Map",
        xlabel='Engine Speed (rpm)',
        ylabel='Torque (lb-ft)',
        is_show=True
    )

```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/heatcurve.png?raw=true)

### Plotting High-Dimensional Heatmaps with Velocity Arrows and Classifications
The `plot_intensity_velocity_and_classes` function creates detailed heatmaps that visualize intensity data with additional features such as velocity vectors, classification patterns, and optional edges. This is particularly useful in fields like geospatial analysis, fluid dynamics, and any area where it's critical to observe how different variables like speed and direction are distributed across a space.

_Functionality_

This function allows for the visualization of scalar fields (intensity data) while superimposing vector fields (velocity data) and categorical overlays (classification patterns). It supports customization of almost every visual aspect, including color maps for intensity and edges, transparency settings, and arrow dynamics. This makes it an invaluable tool for detailed spatial analysis and presentation-ready visualization.

_Parameters_

- **intensity_data** (list of np.array): Contains one or two 2D numpy arrays; the first array represents the intensity values for the heatmap, and the optional second array represents edge intensities.
- **velocity_list** (list of np.array): Contains pairs of numpy arrays representing the components of velocity vectors, either in Cartesian (x and y components) or polar (magnitude and direction) forms.
- **classification_data** (list of np.array): Contains a single numpy array with classification data for each cell, which will be represented as patterns on the heatmap.
- **v_choice** (str): Specifies the format of velocity data ('component' for Cartesian or 'theta' for polar coordinates).
- **primary_colormap, edge_colormap** (str): Colormap identifiers for the intensity and edge data, respectively.
- **edge_thickness** (float): Thickness of the edges around heatmap cells.
- **face_alpha** (float): Transparency for the face colors of heatmap cells.
- **arrow_scale** (float): Scaling factor for the velocity arrows.
- **arrow_colors, arrow_styles, arrow_thicknesses**: Properties for customizing the appearance of velocity arrows.
- **fig_size** (tuple): Dimensions of the figure in inches.
- **face_label, edge_label** (str, optional): Labels for the colorbars of face and edge intensities.
- **class_labels** (list, optional): Custom labels corresponding to each class represented by patterns.
- **is_legend** (bool): Whether to display a legend for classification patterns.
- **is_show** (bool): Whether to display the plot on the screen.
- **save_path** (str, optional): Path to save the plot image file.

_Code Example_

```python
import numpy as np
import multidataplotting as mdp
intensity_data1 = np.random.rand(10, 10)  # Random 10x10 array for cell faces
intensity_data2 = np.random.rand(10, 10)  # Random 10x10 array for cell edges
classification_data = [np.random.randint(0, 4, (10, 10))]  # Random class integers

velocity_x1 = np.random.rand(10, 10) - 0.5
velocity_y1 = np.random.rand(10, 10) - 0.5
velocity_x2 = np.random.rand(10, 10) + 0.5
velocity_y2 = np.random.rand(10, 10) + 0.5

mdp.plot_intensity_velocity_and_classes([intensity_data1, intensity_data2], [velocity_x1, velocity_y1, velocity_x2, velocity_y2],
                                             classification_data,
                                             v_choice='component', primary_colormap='hot', edge_colormap='viridis',
                                             edge_thickness=5, face_alpha=0.5, arrow_scale=0.2,
                                             arrow_colors=['gray', 'black'], arrow_styles=['-', '-'], arrow_thicknesses=[2, 1])
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/VIC.png?raw=true)

### Plotting Contour Maps

The `plot_contour_map` function in the multidataprocessing package generates contour maps based on spatial data, suitable for visualizing gradients, potential fields, or any continuous variable across a two-dimensional area. This function is extremely useful in geophysical studies, meteorology, and landscape ecology to understand topographical, temperature, or pressure variations in a given region.

_Functionality_

Contour maps created by this function help in interpreting complex spatial data by showing lines of equal value, making it easier to see hills, valleys, and plains in geographical data or gradients in any scientific measurements across a surface.

_Parameters_

- **data** (dict or pandas.DataFrame): Data to plot, which should be a dictionary with tuple pairs (x, y) as keys and values representing the measurement at those coordinates, or a DataFrame with columns for x, y, and value.
- **fig_size** (tuple, optional): Dimensions of the figure, typically in inches. Default is (10, 8).
- **title** (str, optional): Title of the contour map. Default is 'Contour Map'.
- **title_fontsize** (int, optional): Font size for the title. Default is 16.
- **xlabel** (str, optional): Label for the x-axis. Default is 'X Coordinate'.
- **ylabel** (str, optional): Label for the y-axis. Default is 'Y Coordinate'.
- **colorbar_label** (str, optional): Label for the colorbar that describes the variable. Default is 'Frequency (%)'.
- **label_fontsize** (int, optional): Font size for the axis labels. Default is 14.
- **tick_fontsize** (int, optional): Font size for the tick labels. Default is 12.
- **contour_levels** (int, optional): Number of contour levels to draw. Default is 20.
- **cmap** (str, optional): Colormap used for the contour plot. Default is 'viridis'.
- **is_contour_line** (bool, optional): Whether to draw contour lines. Default is True.
- **contour_line_colors** (str, optional): Color of the contour lines. Default is 'white'.
- **contour_line_width** (float, optional): Width of the contour lines. Default is 1.0.
- **is_contour_label** (bool, optional): Whether to label the contour lines. Default is True.
- **contour_label_color** (str, optional): Color of the contour labels. Default is 'white'.
- **contour_label_size** (int, optional): Font size of the contour labels. Default is 10.
- **label_interval** (int, optional): Interval at which labels appear on contour lines. Default is 2.
- **save_path** (str, optional): Path to save the figure. If provided, the plot is saved to this location.
- **is_show** (bool, optional): Whether to display the plot. Default is True.
- **xticks** (list, optional): Custom tick intervals for the x-axis.
- **yticks** (list, optional): Custom tick intervals for the y-axis.
- **xtick_labels** (list, optional): Custom labels for the x-axis ticks.
- **ytick_labels** (list, optional): Custom labels for the y-axis ticks.

_Code Example_

```python
import multidataplotting as mdp
import pandas as pd

# Example Data
data = {
    (0, 0): 100, (0, 2): 70,
    (0, 1): 150, (1, 2): 205,
    (1, 0): 200, (2, 1): 160,
    (1, 1): 250, (2, 0): 95,
}

# if using pandas
# data = pd.DataFrame({'Points': [(0,0),(0,1), (0,2),(1,0),(1,1),(1,2),(2,1),(2,0)], 'Elevation': [100, 150, 70, 200, 250, 205, 160, 95]})
# Plotting the contour map
mdp.plot_contour_map(data, title="Elevation Contour Map", xlabel="Longitude", ylabel="Latitude", colorbar_label="Elevation (m)", is_show=True)
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/contour.png?raw=true)

### Plot Density Contours

The `plot_density_contours` function is designed to create visually appealing and informative density contour plots from two-dimensional data points. It is particularly useful for visualizing the distribution and density of dataset features in a spatial context. The function is versatile, with various customizable parameters to suit specific visualization needs.

_Functionality_

This function generates a contour plot that visualizes the density of scattered data points using kernel density estimation. It provides options to adjust the appearance of the plot, including colormap, contour levels, axis labels, and more. The plot can be displayed directly, saved to a file, or both, depending on user preferences.

_Parameters_

- **data** (list of tuples or 2D array): Input data where each tuple contains two elements representing coordinates (x, y).
- **title** (str): Title of the plot. Default is 'Density Contour Plot'.
- **xlabel**, **ylabel** (str): Labels for the x-axis and y-axis, respectively.
- **point_color** (str), **point_size** (int): color and size of scatter points.
- **x_tick_interval**, **y_tick_interval** (float): Specifies the intervals between ticks on the x-axis and y-axis.
- **font_name** (str): Font name for all text in the plot. Default is 'Arial'.
- **font_size** (int): Font size for all text elements in the plot. Default is 12.
- **color_map** (str): Name of the matplotlib colormap used for coloring the plot. Default is 'viridis'.
- **levels** (int): Number of contour levels to plot. Default is 15.
- **convert_to_percent** (bool): If True, converts density values to percentages. Default is True.
- **fig_size** (tuple): Dimensions of the figure in inches (width, height). Default is (10, 8).
- **is_colorbar** (bool): Determines whether to display a color bar. Default is True.
- **save_path** (str): Path where the plot will be saved if provided. Default is None, meaning the plot will not be saved.
- **is_show** (bool): Determines whether to display the plot window. Default is True.

_Code Example_

```python
import numpy as np
import multidataplotting as mdp

# Example usage
data = [(np.random.normal(loc=60, scale=5), np.random.normal(loc=3, scale=1)) for _ in range(100)]
plot_density_contours(data, title='Geysers Eruption Pattern', xlabel='Idle Time (min)', ylabel='Eruption Time (min)',
                      x_tick_interval=5, y_tick_interval=0.5, color_map='plasma', levels=20, convert_to_percent=True,
                      fig_size=(12, 9), is_colorbar=True, save_path='eruption_pattern.png', is_show=True)
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/den_contour.png?raw=true)

### Plotting 3-D Bar Plots

The `plot_3d_stacked_bar` function in the multidataprocessing package creates a three-dimensional stacked bar plot, which is particularly effective for visualizing the distribution of multiple variables across two dimensions with an additional dimension represented by the height of the bars. This type of visualization is useful in finance, sales data analysis, resource allocation, and more, where comparisons across two categorical dimensions are necessary.

_Functionality_

This function enhances data presentation by allowing for the visualization of complex interrelationships among data in a three-dimensional space, making it easier to discern patterns and trends that may not be as obvious in two-dimensional plots.

_Parameters_

- **pair_freq** (dict or pandas.DataFrame): Data to plot, either as a dictionary with tuple pairs (x, y) as keys and values as their frequency, or a DataFrame with suitable columns.
- **x_bin_ticks** (list): Bins or categories for the x-axis.
- **y_bin_ticks** (list): Bins or categories for the y-axis.
- **fig_size** (tuple, optional): Dimensions of the figure, typically in inches. Default is (12, 10).
- **title** (str, optional): Title of the 3D plot. Default is '3D Stacked Bar Plot'.
- **title_fontsize** (int, optional): Font size for the title. Default is 16.
- **xlabel** (str, optional): Label for the x-axis. Default is 'Variable 1'.
- **ylabel** (str, optional): Label for the y-axis. Default is 'Variable 2'.
- **zlabel** (str, optional): Label for the z-axis, representing the frequency or another measured variable. Default is 'Frequency'.
- **is_percent** (bool, optional): Whether to display the z-axis values as percentages. Default is False.
- **label_fontsize** (int, optional): Font size for the axis labels. Default is 10.
- **tick_fontsize** (int, optional): Font size for the tick labels. Default is 10.
- **color_map** (matplotlib.colors.Colormap, optional): Color map for the bars, affecting their color based on value. Default uses Matplotlib's viridis.
- **save_path** (str, optional): Path to save the figure. If provided, the plot is saved to this location.
- **is_show** (bool, optional): Whether to display the plot. Default is True.
- **x_ticklabel_left_close** (bool, optional): Whether to close the left side of x-tick labels. Default is False.
- **x_ticklabel_right_close** (bool, optional): Whether to close the right side of x-tick labels. Default is False.
- **y_ticklabel_top_close** (bool, optional): Whether to close the top side of y-tick labels. Default is False.
- **y_ticklabel_bottom_close** (bool, optional): Whether to close the bottom side of y-tick labels. Default is False.
- **elevation** (int, optional): Elevation angle of the 3D view. Default is 30.
- **azimuth** (int, optional): Azimuth angle of the 3D view. Default is 30.
- **background_color** (str, optional): Background color of the plot. Default is 'white'.

_Code Example_

```python
import multidataplotting as mdp

# Example data: Sales volume for different regions and product categories
data = {
    (0, 0): 100, (0, 2): 70,
    (0, 1): 150, (1, 2): 205,
    (1, 0): 200, (2, 1): 160,
    (1, 1): 250, (2, 0): 95,
}

# Defining the categories for the axes
x_categories = ["Reg 1", "Reg 2"]
y_categories = ["Prod A", "Prod B"]

# Plotting the 3D stacked bar chart
mdp.plot_3d_stacked_bar(data, x_bin_ticks=x_categories, y_bin_ticks=y_categories, \
    elevation = 65, azimuth = 120, ytick_rotation=60,
        title="Annual Sales Volume", xlabel="Region", ylabel="Product Category", zlabel="Sales Volume", is_show=True)
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/3DStackbar.png?raw=true)

### Polynomial Surface Fit and Visualization

The `plot_surface_with_residuals` function in our data visualization toolkit enables the fitting of a polynomial surface to three-dimensional data points and provides detailed visualization of the results. This tool is particularly useful for professionals in environmental science, geophysics, and engineering who need to analyze spatial distributions and surface patterns.

#### Functionality

This function fits a polynomial surface to provided 3D data points (x, y, z) and visualizes the surface along with the original data and calculated residuals. It offers high customization flexibility, allowing users to tailor plot elements such as color, transparency, markers, and lines to their specific needs.

#### Parameters

- **x_data**, **y_data**, **z_data** (arrays): The x, y, and z coordinates of the data points.
- **xlabel**, **ylabel**, **zlabel** (str, optional): Labels for the x, y, and z axes. Defaults are 'X', 'Y', 'Z'.
- **x_tick_interval**, **y_tick_interval**, **z_tick_interval** (float, optional): Specifies the intervals between ticks on the respective axes.
- **tick_fontsize** (int, optional): Font size for the tick labels.
- **line_color** (str, optional): Color of the lines used for residuals.
- **line_thickness** (int, optional): Thickness of the residual lines.
- **dot_color** (str, optional): Color of the data point markers.
- **dot_size** (int, optional): Size of the data point markers.
- **surface_cmap** (str, optional): Color map for the surface plot.
- **alpha** (float, optional): Transparency of the surface plot.
- **is_legend** (bool, optional): Toggle to display a legend on the plot.
- **legend_loc** (str, optional): Location of the legend on the plot.
- **is_show** (bool, optional): Toggle to display the plot immediately after generation.
- **save_path** (str, optional): File path where the plot image will be saved, if specified.

#### Code Example

```python
import numpy as np
import multidataplotting as mdp

np.random.seed(0)
x_example = np.random.uniform(-5, 5, 50)
y_example = np.random.uniform(-5, 5, 50)
z_example = 3 + 1*x_example - 2*y_example + 1*x_example**2 - 1.5*y_example**2 + 0.5*x_example*y_example + np.random.normal(0, 10, 50)
mdp.plot_surface_with_residuals(x_example, y_example, z_example, dot_color = 'black', line_color='gray', x_tick_interval=3)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/surface.png?raw=true)

### Timeline Plotting Function

The `plot_timeline` function in our Python library is designed to create detailed, customizable timeline charts. This function is ideal for visualizing historical events, project timelines, or any sequential data where the timing and duration of events are crucial.

_Functionality_

This function generates a timeline chart from a list of time intervals, providing extensive customization options for labeling, color schemes, time resolutions, and more. It's suitable for a wide range of applications, from historical timelines to project management and planning.

_Parameters_

- **data** (list of tuples): Each tuple contains two elements, the start and end times of an event, formatted as strings or datetime objects.
- **title** (str): Title of the chart. Default is "Historical Timeline".
- **time_resolution** (str): Defines the granularity of the timeline, such as 'y' for years, 'm' for months, etc. Default is 'y'.
- **label_format** (str or None): Optional. If a string is provided, labels are generated with this string as a prefix followed by an incrementing number. If None, no labels are applied.
- **time_interval** (int): The interval between major ticks on the timeline, corresponding to the `time_resolution`. Default is 2.
- **is_grid** (bool): If True, displays a grid on the timeline. Default is True.
- **is_show** (bool): If True, shows the plot. If False, the plot is not displayed unless saved. Default is True.
- **save_path** (str or None): If provided, the plot is saved to the specified path. Default is None.
- **fig_size** (tuple): Figure dimensions in inches, as (width, height). Default is (15, 8).
- **color_palette** (str): Name of the matplotlib colormap to use for coloring the timeline bars. Default is 'tab20'.
- **label_color** (str): Color of the labels. Default is 'black'.
- **label_font_size** (int): Font size of the labels. Default is 10.
- **label_font_name** (str): Font name of the labels. Default is 'Arial'.

_Code Example_

```python
import multidataplotting as mdp

data = [
    ("2021-01-01T00:00:00", "2021-12-31T23:59:59"),
    ("2022-01-01T00:00:00", "2022-12-31T23:59:59"),
    ("2020-05-01T00:00:00", "2023-12-31T23:59:59")
]
mdp.plot_timeline(data, title="Detailed Timeline", time_resolution='m', label_format="Period",
              time_interval=3, is_grid=True, is_show=True, save_path='detailed_timeline.png', fig_size=(15, 8),
              color_palette='tab20', label_color='black', label_font_size=12, label_font_name='Arial')


```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/timeline.png?raw=true)

### Radar Chart Visualization

The `plot_radar_chart` function in our data visualization toolkit enables the creation of radar (or spider) charts, which are excellent for displaying multivariate observations with an arbitrary number of variables. This type of visualization is particularly useful in fields like product management, marketing analysis, and other areas where performance metrics across different categories need to be compared visually.

_Functionality_

This function generates a radar chart from a provided DataFrame, with each column representing a different series and the DataFrame index used as category labels. The radar chart supports extensive customization for the visual elements such as color, line styles, and markers, allowing each series to be distinct or uniformly styled.

_Parameters_

- **data** (pd.DataFrame): The DataFrame containing the data to be plotted. Each column is treated as a separate series.
- **fig_size** (tuple, optional): Figure dimensions in inches.
- **tick_font_size** (int, optional): Font size for tick labels.
- **tick_font_name** (str, optional): Font name for tick labels.
- **title** (str, optional): Title of the chart.
- **title_font_size** (int, optional): Font size for the title.
- **title_font_name** (str, optional): Font name for the title.
- **is_legend** (bool, optional): Toggle to display the legend.
- **is_show** (bool, optional): Toggle to immediately show the plot.
- **save_path** (str, optional): If provided, the path where the plot will be saved.
- **color_choice** (str or list, optional): Color map name or a list of colors for each series.
- **line_style** (str or list, optional): Line style, can be a single style or a list to apply to each series.
- **line_thickness** (float or list, optional): Line thickness, can be a single value or a list for each series.
- **marker_size** (int or list, optional): Size of the markers, can be a single value or a list for each series.
- **marker_type** (str or list, optional): Type of the markers, can be a single type or a list for each series.
- **marker_color** (str or list, optional): Color of the markers, can be a single color or a list for each series.

_Code Example_

```python
np.random.seed(0)
data = pd.DataFrame({
    'Spring': np.random.rand(5),
    'Summer': np.random.rand(5),
    'Autumn': np.random.rand(5),
    'Winter': np.random.rand(5),
}, index=['Taste', 'Cost', 'Sustainability', 'Nutrition', 'Convenience'])

# Define individual properties for each category
colors = ['red', 'green', 'blue', 'purple']  # Color for each series
line_styles = ['-', '--', '-.', ':']  # Line style for each series
line_thicknesses = [2, 2.5, 3, 3.5]  # Line thickness for each series
marker_sizes = [8, 10, 12, 14]  # Marker size for each series
marker_types = ['o', '^', 's', 'p']  # Marker type for each series
marker_colors = ['black', 'orange', 'cyan', 'yellow']  # Marker color for each series

# Plot using lists for properties
mdp.plot_radar_chart(data, fig_size=(8, 8), tick_font_size=12, tick_font_name='Arial',
                 title="Seasonal Product Analysis", title_font_size=16, title_font_name='Arial',
                 is_legend=True, is_show=True, save_path=None,
                 color_choice=colors, line_style=line_styles,
                 line_thickness=line_thicknesses,
                 marker_size=marker_sizes, marker_type=marker_types,
                 marker_color=marker_colors)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/radar_chart.png?raw=true)

### Draw Grouped Polar Bars

The `draw_grouped_polar_bars` function in our visualization toolkit provides a sophisticated method for displaying grouped polar bar plots. This function is designed to plot data across different groups with an aesthetically pleasing circular layout, which is ideal for comparative analysis in fields like meteorology, biology, or market segmentation studies.

_Functionality_

This function is adept at illustrating complex datasets in a circular (polar) bar plot format. It enables the visualization of distinct groups with unique color codings, and supports adding optional labels for each bar, custom radial ticks, and group labels positioned strategically within the plot.

_Parameters_

- **groups** (list of np.array): A list where each array corresponds to a group's data points.
- **group_names** (list of str): Labels for each group, displayed around the plot.
- **group_colors** (list of str): Colors assigned to each group for distinction.
- **label_names** (list of str, optional): Labels for each bar within the groups. Default is `None`.
- **fig_size** (tuple, optional): Dimensions of the figure in inches. Default is `(8, 8)`.
- **scale_lim** (int, optional): The limit for the radial scale marking. Default is `100`.
- **scale_major** (int, optional): The major tick interval on the radial scale. Default is `20`.
- **tick_font_size** (int, optional): Font size for the tick labels. Default is `5`.
- **label_font_size** (int, optional): Font size for the bar labels. Default is `5`.
- **save_path** (str, optional): Path to save the generated plot image. Default is `None`.
- **is_show** (bool, optional): Whether to display the plot on screen. Default is `True`.

_Code Example_

```python

import numpy as np
import multidataplotting as mdp

np.random.seed(123)
group1 = 100 * np.random.rand(5)
group2 = 100 * np.random.rand(5)
group3 = 100 * np.random.rand(5)
group4 = 100 * np.random.rand(5)
group5 = 100 * np.random.rand(5)
 
groups = [group1, group2, group3, group4, group5]
group_names = list('ABCDE')
group_colors = ['#d7191c','#fdae61','#ffffbf','#abd9e9','#2c7bb6']

labels = ["MN","WI","MI","IA","IN"]
    
mdp.draw_grouped_polar_bars(groups, group_names, group_colors, label_names=labels) 

```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/polarbar.png?raw=true)

### Plotting Rose Map

The `plot_rose_map` function in the multidataprocessing package creates a rose diagram (or wind rose), which is commonly used in meteorology to display the frequency of occurrence of events relative to multiple directions. This visualization is also highly effective in geography, environmental science, and any field requiring the analysis of directional data.

_Functionality_

This function facilitates the analysis of how often events occur from different directions and can include an additional dimension representing magnitude (such as wind speed) or frequency. It's perfect for visualizing how wind direction and speed vary at a particular location or how any directional data is distributed.

_Parameters_

- **input_data** (pd.DataFrame): The DataFrame containing the data. It should include columns for direction (degrees or category) and the value or frequency of occurrences.
- **key_1** (str): Column name in input_data for directional data.
- **key_2** (str): Column name in input_data for the values associated with each direction.
- **interval** (int, optional): The bin size for directional data, in degrees. Default is 10.
- **value_interval** (int, optional): The bin size for value data, providing granularity in how values are segmented within the plot. Default is None, which means no binning.
- **title** (str, optional): Title of the rose map. Default is "Rose Map".
- **label_size** (int, optional): Font size for the labels on the plot. Default is 12.
- **label_interval** (int, optional): Interval for displaying labels around the rose, which can help in reducing label clutter. Default is 1.
- **color_ramp** (str, optional): Color map used for the plot. Default is "viridis".
- **tick_label_size** (int, optional): Font size for the tick labels. Default is 12.
- **tick_label_color** (str, optional): Color for the tick labels. Default is 'black'.
- **tick_font_name** (str, optional): Font name for the tick labels. Default is 'Arial'.
- **fig_size** (tuple, optional): Dimensions of the plot, in inches. Default is (10, 8).
- **colorbar_label** (str, optional): Label for the color bar. Default is "Intensity".
- **colorbar_label_size** (int, optional): Font size for the color bar label. Default is 12.
- **max_radius** (float, optional): Maximum radius for the plot, controlling how far out the data extends. Default is None, which auto-scales.
- **save_path** (str, optional): File path where the plot will be saved, if desired.
- **is_show** (bool, optional): Whether to display the plot. Default is True.

_Code Example_

```python
import pandas as pd
import multidataplotting as mdp

# Example wind data
data = {
    'Direction': [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
    'Speed': [5, 10, 15, 20, 15, 10, 5, 10, 15, 20, 25, 30]
}
df = pd.DataFrame(data)

# Plotting the wind rose
mdp.plot_rose_map(df, key_1='Direction', key_2='Speed', interval=30, title="Wind Rose Diagram", color_ramp='plasma', is_show=True)
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/rosemap.png?raw=true)

### Circular Bar Chart Function

The `plot_cyclic_bar` function in our advanced data visualization toolkit offers a robust method for displaying circular bar charts (or donut charts). This tool is perfect for visualizing relative proportions of categories or metrics in a format that is both visually engaging and informative. It is particularly useful in fields such as market analysis, performance tracking, and health data visualization, where understanding the distribution and magnitude of contributions is crucial.

_Functionality_

This function enables the creation of multilayered circular bar charts with a high degree of customization. It provides options for adjusting colors, dimensions, text styling, and more, allowing users to tailor the visualization to their specific needs. Key features include adjustable ring sizes, customizable start angles, and the option to save or display the plot directly.

_Parameters_
- **data** (pd.DataFrame): Data containing the values to be plotted, with indexes used as labels.
- **r0** (float): Radius of the innermost circle.
- **delta** (float): Thickness of each ring.
- **fig_size** (tuple, optional): Dimensions of the figure, defaulting to `(5, 5)`.
- **color_list** (list, optional): List of colors for each ring; a default palette is provided.
- **start_angle** (int, optional): Starting angle for the first segment, default is 90 degrees.
- **edge_color** (str, optional): Color of the edge between segments, default is 'white'.
- **text_offset** (float, optional): Vertical offset for the text inside the rings, default is 0.02.
- **font_size** (int, optional): Font size for labels, default is 10.
- **font_name** (str, optional): Font family for labels, default is 'sans-serif'.
- **label_color** (str, optional): Color of the text labels, default is 'black'.
- **non_filled_color** (str, optional): Color for the non-filled area of each ring, default is 'lightgrey'.
- **is_show** (bool, optional): If `True`, displays the plot; default is True.
- **save_path** (str, optional): If provided, saves the plot to the specified path with high resolution.

_Code Example_

```python
import pandas as pd
import multidataplotting as mdp

data = pd.DataFrame({
    'Values': [280, 400, 900, 200, 700, 450, 550, 420, 780]
}, index=['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry', 'Melon', 'Pineapple', 'Kiwi', 'Mango'])

mdp.plot_cyclic_bar(data, r0=2, delta=0.1)
```

![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/cycbar.png?raw=true)

### Plotting Rose Contour Map for Directional Data

The `plot_rose_contour_map` function creates a rose contour map to visualize directional data using contours with optional threshold-based boundary lines. This is particularly useful in meteorology, oceanography, and environmental sciences where wind, waves, or any directional data need to be visualized for analysis and decision-making.

_Functionality_

This function plots a rose (or wind) contour map with options for customization such as color ramps, boundary lines at specified density thresholds, and percentage labels. It supports various contour levels, providing flexibility for detailed and high-level data representation.

_Parameters_

- **input_data** (pd.DataFrame): The DataFrame containing the directional data.
- **key_1** (str): The column name for directional data.
- **key_2** (str): The column name for the value data.
- **title** (str): Title of the plot.
- **label_size** (int): Font size for labels.
- **color_ramp** (str): Color ramp for the plot.
- **fig_size** (tuple): Size of the figure.
- **num_levels** (int): Number of contour levels.
- **max_radius** (float): Maximum radius of the plot.
- **density_threshold** (float): Density threshold for boundary line.
- **z_label** (str): Label for the colorbar.
- **boundary_line_color** (str): Color for the boundary line.
- **boundary_line_thickness** (float): Thickness of the boundary line.
- **is_percent** (bool): Whether to show the colorbar as a percentage.
- **tick_spacing** (int): Spacing between ticks on the colorbar.
- **save_path** (str): Path to save the plot.
- **is_show** (bool): Whether to display the plot.

_Code Example_

Suppose you are analyzing wind data and need to visualize the distribution and intensity of wind directions:

```python
import pandas as pd
import multidataplotting as mdp
data = pd.DataFrame({
    'direction': np.random.randint(0, 360, 1000),
    'speed': np.random.rand(1000) * 100
})
mdp.plot_rose_contour_map(data, 'direction', 'speed', color_ramp='plasma', num_levels=10, density_threshold=0.001,
                      boundary_line_color='red', boundary_line_thickness=3, is_percent = True)
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/rosecontourmap.png?raw=true)

### Plotting Cumulative Distribution Functions
The plot_cdfs function generates cumulative distribution function (CDF) plots for multiple datasets. It is designed for versatile statistical analysis, useful in fields such as finance, engineering, and scientific research, where understanding the distribution of data is crucial.

_Functionality_

This function can plot the CDFs of multiple datasets either on a single figure or across multiple subplots. It offers extensive customization options, including line styles, colors, markers, and more. Optional logarithmic scaling for the x-axis accommodates data that spans several orders of magnitude.

_Parameters_

- **data_lists** (list of lists): Each sublist contains data points for which the CDF will be plotted.
- **fig_size** (tuple, optional): Dimensions of the figure in inches. Default is (10, 6).
- **line_styles** (dict, optional): Styles of the plot lines for each dataset. Default is solid lines.
- **line_widths** (dict, optional): Widths of the plot lines for each dataset. Default is 1.
- **is_percent** (bool, optional): Whether to plot the CDF values in percentage. Default is True.
- **line_colors** (dict, optional): Colors of the plot lines for each dataset. Default is blue.
- **legends** (list, optional): Legend labels for each dataset. Default labels are 'Data 1', 'Data 2', etc.
- **marker_colors** (dict, optional): Colors of the markers for each dataset. Matches line colors by default.
- **x_tick_interval** (int, optional): Interval between x-axis ticks. Default is 10.
- **tick_label_fontsize** (int, optional): Font size for tick labels. Default is 12.
- **markers** (dict, optional): Marker styles for each dataset. Default is None.
- **show_grid** (bool, optional): Whether to show grid lines. Default is True.
- **font_name** (str, optional): Font family for all text elements. Default is 'Arial'.
- **font_size** (int, optional): Font size for all text elements. Default is 12.
- **save_path** (str, optional): File path to save the plot image, if desired. Default is None.
- **dpi** (int, optional): Resolution of the saved plot image. Default is 100.
- **is_same_figure** (bool, optional): Whether to plot all CDFs on the same figure. Default is True.
- **is_log_x** (bool, optional): Whether to use logarithmic scaling for the x-axis. Default is False.
- **regression_trans** (list of tuples, optional): Ranges for which to perform OLS regression. Default is None.
- **title** (str, optional): Title of the plot. Default is 'Cumulative Distribution Function'.
- **show_reg_eqn** (bool, optional): Whether to display the regression equation. Default is True.
- **annno_digits** (int, optional): Number of digits after the decimal in the regression equation annotation. Default is 3.

_Code Example_
```python
import numpy as np
import multidataplotting as mdp
# Generate random data for three datasets
np.random.seed(0)  # For reproducibility
data1 = np.random.normal(50, 10, 200)
data2 = np.random.exponential(scale=30, size=200)
data3 = np.random.lognormal(mean=2, sigma=0.5, size=200)

data_lists = [data1, data2, data3]

# Define regression ranges for each dataset
# Assuming each tuple corresponds to a specific dataset's regression range
regression_ranges = [(45, 55), (20, 40), (7, 11)]

# Call your plotting function with regression analysis
plot_cdfs(data_lists, line_colors={0: 'red', 1: 'blue', 2: 'green'},
          regression_trans=regression_ranges, is_log_x = True,
          legends=['Normal Distribution', 'Exponential Distribution', 'Lognormal Distribution'])

```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/newCDFs.png?raw=true)

### Plotting Positive and Negative Dot Plots
The plot_pos_neg_dot_plot function in the visualization toolkit is specifically designed to create scatter plots that visually distinguish between positive and negative data points over a set of years. This feature is particularly useful in fields like finance, environmental science, and public health, where it is crucial to track and compare upward and downward trends over time.

_Functionality_

This function is ideal for illustrating trends where data points are categorized into positive and negative groups across time. It can be used to visualize earnings vs. losses, growth vs. decline, or any other dataset where such distinctions are meaningful. The clear visualization aids in quick assessment and comparative analysis of data trends.

_Parameters_

- **positive** (array-like): Array of positive values.
- **negative** (array-like): Array of negative values.
- **years** (array-like): Array of years corresponding to the values.
- **marker_size** (int, optional): Size of the markers. Default is 100.
- **marker_type** (str, optional): Type of the markers (e.g., 'o' for circles, '*' for stars). Default is 'o'.
- **alpha** (float, optional): Transparency of the markers. Default is 1.0.
- **tick_font_name** (str, optional): Font name for the tick labels. Default is 'Arial'.
- **tick_font_size** (int, optional): Font size for the tick labels. Default is 12.
- **positive_color** (str, optional): Color for positive value markers. Default is 'blue'.
- **negative_color** (str, optional): Color for negative value markers. Default is 'red'.
- **title** (str, optional): Title of the plot. Default is 'Example Dot Plot'.
- **xlabel** (str, optional): Label for the x-axis. Default is 'Year'.
- **ylabel** (str, optional): Label for the y-axis. Default is 'Value'.
- **y_limits** (tuple, optional): Minimum and maximum limits for the y-axis. If None, defaults to [-25, 25].
- **fig_size** (tuple, optional): Size of the figure in inches. Default is (10, 5).
- **is_show** (bool, optional): Whether to display the plot. Default is True.
- **is_legend** (bool, optional): Whether to display a legend. Default is False.
- **positive_label** (str, optional): Legend label for positive values. Default is 'Positive'.
- **negative_label** (str, optional): Legend label for negative values. Default is 'Negative'.
- **save_path** (str, optional): Path to save the plot image file. If None, the plot is not saved.

_Code Example_

```python
import numpy as np
import multidataplotting as mdp
positive = np.random.randint(0, 20, 100)
negative = np.random.randint(0, 20, 100)
years = np.arange(100)  # Example years
mdp.plot_pos_neg_dots(positive, negative, years, marker_type='o', positive_color='green', negative_color='orange', alpha=0.5,
            positive_label='Gain', negative_label='Loss', is_legend=True, save_path='custom_plot.png')
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/PosNegDots.png?raw=true)

### Plot Movement Arrows

The `plot_movement_arrows` function in the visualization package is designed to illustrate changes or movements between two datasets across different dimensions. This function is particularly useful in displaying dynamic changes in data, represented by arrows that indicate direction and magnitude of changes from one period or condition to another.

_Functionality_

This function plots initial data points from a starting dataset and draws arrows pointing towards the corresponding points in a subsequent dataset. It supports log-scaled axes for better visualization of data spanning several orders of magnitude.

_Parameters_

- **pre_data** (dict): Data points from the initial dataset. Each key should correspond to a label and map to a tuple `(x, y)`.
- **post_data** (dict): Data points from the subsequent dataset. Format similar to `pre_data`.
- **labels** (list of str): Labels that identify each data point. These labels are used for annotations and must correspond to keys in `pre_data` and `post_data`.
- **title** (str): Title of the plot. Default is 'Movement Over Time'.
- **xlabel**, **ylabel** (str): Labels for the x-axis and y-axis.
- **x_delta**, **y_delta** (float): Margins added to x and y axes limits to ensure all data and annotations are visible.
- **arrow_color** (str): Color of the arrows depicting movement.
- **scale** (float): Scale factor for arrows to control their size and visibility.
- **fig_size** (tuple): Dimensions of the figure.
- **use_log_x**, **use_log_y** (bool): Flags to apply logarithmic scale on x or y axes.
- **is_show** (bool): Flag to display the plot immediately.
- **is_grid** (bool): Flag to display grid lines on the plot.
- **save_path** (str): Path to save the figure. If provided, the plot is saved to this path.
- **font_name** (str), **font_size** (int): Font settings for titles and labels.
- **annotation_text_size** (int), **annotation_text_color** (str): Settings for annotation text properties.

_Code Example_

```python
import multidataplotting as mdp

data_1980 = {
    'New York': (8e6, 5.5),
    'San Francisco': (800000, 6.0),
    'Chicago': (2.7e6, 5.0)
}
data_2015 = {
    'New York': (8.5e6, 6.5),
    'San Francisco': (900000, 7.5),
    'Chicago': (2.7e6, 5.7)
}
labels = ['New York', 'San Francisco', 'Chicago']

mdp.plot_movement_arrows(data_1980, data_2015, labels, x_delta = 200000, use_log_x=True)
```
![alt text](https://github.com/wwang487/MultiDataPlotting/blob/main/picture/moving_arrow.png?raw=true)
