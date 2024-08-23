"""
This module has content for generating plots
"""

import random
from pathlib import Path
from typing import cast

import logging

logging.getLogger("matplotlib").setLevel(logging.WARNING)
import matplotlib  # NOQA

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # NOQA
import matplotlib as mpl  # NOQA


class PlotSeries:

    def __init__(self, label: str = ""):
        self.label = label


class LinePlotSeries(PlotSeries):
    def __init__(self, x: list[float], y: list[float], label: str = "") -> None:
        super().__init__(label)
        self.x = x
        self.y = y


class MatplotlibPlotter:

    def __init__(self):
        self.ax = plt.subplot(111)

    def set_decorations(self, x_label, y_label, title, x_ticks, y_ticks):
        self.ax.legend(loc="upper left")
        if x_label:
            self.ax.set_xlabel(x_label)
        if y_label:
            self.ax.set_ylabel(y_label)
        if title:
            self.ax.set_title(title)
        if x_ticks:
            self.ax.set_xticks(x_ticks)
        if y_ticks:
            self.ax.set_yticks(y_ticks)

    def plot_line(self, x, y, label, color):
        self.ax.plot(x, y, label=label, color=color)

    def render(self, path: Path | None = None):
        if path:
            plt.savefig(path)
        else:
            plt.show()


class Plot:
    def __init__(
        self,
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        legend_label: str = "",
    ) -> None:
        self.series: list[PlotSeries] = []
        self.title = title
        self.plot_type = ""
        self.x_label = x_label
        self.y_label = y_label
        self.legend_label = legend_label
        self.c_map = mpl.colormaps["viridis"]
        self.x_ticks = None
        self.y_ticks = None
        self.impl = MatplotlibPlotter()

    def get_colour(self, curr, values, c_map):
        """
        Returns a colour based on a cmap and how far across
        the datasets you are
        """
        length = len(values)
        position = curr / length
        return c_map(0.25 + (position / 2))

    def set_colour_map(self, cmap="viridis"):
        self.c_map = mpl.colormaps[cmap]

    def set_x_ticks(self, lower, upper, step):
        self.x_ticks = range(lower, upper + 1, step)

    def set_y_ticks(self, lower, upper, step):
        self.y_ticks = range(lower, upper + 1, step)

    def set_decorations(self):
        self.impl.set_decorations(
            self.x_label, self.y_label, self.title, self.x_ticks, self.y_ticks
        )

    def plot(self, path: Path | None = None):
        raise NotImplementedError()


class LinePlot(Plot):

    def plot(self, path: Path | None = None):

        first = True
        for i, series in enumerate(self.series):
            colour = self.get_colour(i, self.series, self.c_map)
            label = f"{series.label}"
            if first and self.legend_label:
                label = f"{label} {self.legend_label}"
                first = False
            line_series = cast(LinePlotSeries, series)
            self.impl.plot_line(line_series.x, line_series.y, label=label, color=colour)

        self.set_decorations()
        self.impl.render(path)


class MultiFigureLinePlotter:
    """
    Plot with multiple figures. Each is a line plot
    """

    def __init__(self, data: dict, figures: list, xlabel: str) -> None:
        self.data = data
        self.figures = figures
        self.size: tuple = (10, 5)
        self.xlabel = xlabel
        self.output_fmt = "svg"

    def _plot_line(self, key: str, label: str):
        plt.plot(self.data[key], label=label)

    def _decorate(self, ylabel: str, title: str):
        plt.title(title)
        plt.xlabel(self.xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.show()

    def plot(self, output_path: Path):
        """
        Do the plot
        """

        for idx, figure_info in enumerate(self.figures):
            plt.figure(figsize=self.size)

            for data_key, label in zip(figure_info["keys"], figure_info["labels"]):
                self._plot_line(data_key, label)

            title = figure_info["title"]
            ylabel = figure_info["ylabel"]

            self._decorate(ylabel, title)
            plt.savefig(str(output_path) + f"_{idx}.{self.output_fmt}")


class DatasetGridPlotter:
    """
    Plot a dataset on a grid. A dataset has pairs of images corresponding
    to an image and an associated mask.
    """

    def __init__(
        self, title: str = "", stride: int = 4, size: tuple = (25, 20)
    ) -> None:
        self.title = title
        self.stride = stride
        self.size = size

    def _plot_grid_element(self, rows: int, cols: int, count: int, image, transform):
        plt.subplot(rows, cols, count)
        if transform:
            plt.imshow(transform.reverse(image.squeeze(0).float()))
        else:
            plt.imshow(image.squeeze(0).float())
        plt.axis("off")
        plt.title(self.title)
        return count + 1

    def plot(self, data, num_samples: int, output_path: Path, transform=None):
        plt.figure(figsize=self.size)
        rows = num_samples // self.stride
        cols = num_samples // rows
        count = 1
        indices = [random.randint(0, len(data) - 1) for _ in range(num_samples)]

        for index in indices:
            if count == num_samples + 1:
                break
            x, y = data[index]
            count = self._plot_grid_element(rows, cols, count, x, transform)
            count = self._plot_grid_element(rows, cols, count, y, transform)
        plt.savefig(output_path)
