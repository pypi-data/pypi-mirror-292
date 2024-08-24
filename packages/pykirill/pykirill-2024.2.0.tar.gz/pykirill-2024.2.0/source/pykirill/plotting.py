"""
Plotting utility functions
"""

import logging
import math
import typing

import matplotlib.font_manager
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from numpy import typing as npt

from . import moods

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup() -> None:
    """
    Configures the default settings for Seaborn and Matplotlib, including theme, style, color palette,
    font settings, and IPython-specific configurations if available.

    - Sets the Seaborn theme to 'notebook' context with 'whitegrid' style and 'colorblind' palette.
    - Sets Matplotlib's default colormap to 'viridis' and enables figure autolayout.
    - Attempts to set the default font to Arial if available; otherwise defaults to sans-serif.
    - Configures IPython to use inline plotting and retina display if IPython is present and running.
    """

    sns.set_theme(context="notebook", style="whitegrid", palette="colorblind")
    plt.rcParams["image.cmap"] = "viridis"
    plt.rcParams["figure.autolayout"] = True

    arial_available = False
    for font in matplotlib.font_manager.fontManager.ttflist:
        if "Arial" in font.name:
            arial_available = True
            break

    if arial_available:
        plt.rcParams["font.family"] = "Arial"
        logger.info("Arial font is available and has been set as the default font.")
    else:
        plt.rcParams["font.family"] = "sans-serif"
        logger.info("Arial font is not available. Defaulting to sans-serif font.")

    try:
        import IPython
    except ImportError:
        logger.info("IPython is not installed, IPython-specific configurations are skipped.")
        return

    ipython = IPython.get_ipython()
    if not ipython:
        logger.info("Not running in an IPython environment. IPython-specific configurations are skipped.")
        return

    ipython.run_line_magic("matplotlib", "inline")
    ipython.run_line_magic("config", "InlineBackend.figure_format = 'retina'")

    logger.info(moods.generate_notebook_string())


class SubplotsManager:
    """
    Manages the creation and iteration of subplots in a Matplotlib figure.

    Attributes:
        ROWS_SCALING_FACTOR: Scaling factor for the height of each row.
        COLUMNS_SCALING_FACTOR: Scaling factor for the width of each column.
        MAXIMUM_DIMENSIONS_IN_ONE_ROW: Maximum number of subplots in one row.
        figure: The Matplotlib figure containing the subplots.
        axes: Array of Matplotlib Axes objects representing the subplots.
        n_plots: The total number of subplots.
        n_rows: The number of rows of subplots.
        n_columns: The number of columns of subplots.
        figure_size: The size of the figure (width, height).
        current_iteration_index The index of the next subplot to be accessed.

    Usage:
        ```python
        axm = plotting.SubplotsManager(4)

        for trajectory_fragment in range(4):
        frame_values = ...

        ax = axm.nextax()
        ax.hist(frame_values)
        ax.set_title(f"Histogram of intensity values of {trajectory_fragment}")
        ax.set_xlabel("Intensity")
        ax.set_ylabel("Frequency")

        axm.show()
        ```
    """

    ROWS_SCALING_FACTOR: int = 5
    COLUMNS_SCALING_FACTOR: int = 6
    MAXIMUM_DIMENSIONS_IN_ONE_ROW: int = 5

    def __init__(self, dimensions: int | tuple[int, int], figure_size: typing.Optional[tuple[int, int]] = None) -> None:
        """
        Initializes the SubplotsManager with the given dimensions and optional figure size.

        Args:
            dimensions: The number of subplots or a tuple specifying (rows, columns).
            figure_size: The size of the figure (width, height). Defaults to None.
        """

        self.n_rows: int
        self.n_columns: int
        self.n_plots: int

        self.figure: plt.Figure
        self.axes: npt.NDArray[typing.Any]

        self.n_rows, self.n_columns, self.n_plots = self.calculate_dimensions(dimensions)

        if figure_size is None:
            self.figure_size = (
                self.COLUMNS_SCALING_FACTOR * self.n_columns,
                self.ROWS_SCALING_FACTOR * self.n_rows,
            )
        else:
            self.figure_size = figure_size

        self.figure, self.axes = self.create_subplots(self.n_rows, self.n_columns, self.figure_size)
        self.current_iteration_index: int = 0

    def calculate_dimensions(self, dimensions: int | tuple[int, int]) -> tuple[int, int, int]:
        """
        Calculates the number of rows and columns for the subplots based on the given dimensions.

        Args:
            dimensions: The number of subplots or a tuple specifying (rows, columns).

        Returns:
            The number of rows, columns, and total number of plots.
        """

        if isinstance(dimensions, tuple):
            n_rows, n_columns = dimensions
            n_plots = n_rows * n_columns
            return n_rows, n_columns, n_plots

        if isinstance(dimensions, int):
            if dimensions <= self.MAXIMUM_DIMENSIONS_IN_ONE_ROW:
                return 1, dimensions, dimensions

            n_columns = math.ceil(math.sqrt(dimensions))
            n_rows = math.ceil(dimensions / n_columns)
            return n_rows, n_columns, dimensions

        raise ValueError("Dimensions must be int or tuple")

    def create_subplots(
        self, n_rows: int, n_columns: int, figure_size: tuple[int, int]
    ) -> tuple[plt.Figure, npt.NDArray[typing.Any]]:
        """
        Creates the subplots and returns the figure and axes array.

        Args:
            n_rows: The number of rows of subplots.
            n_columns: The number of columns of subplots.
            n_plots: The total number of subplots.
            figure_size: The size of the figure (width, height).

        Returns:
            The figure and axes array.
        """

        fig, axes = plt.subplots(n_rows, n_columns, figsize=figure_size)
        if isinstance(axes, np.ndarray):
            axes = axes.flatten()
        else:
            axes = np.array([axes])
        return fig, axes

    def show(self) -> None:
        """
        Displays the figure with a tight layout.
        """

        self.figure.tight_layout()
        plt.show()

    def nextax(self) -> typing.Optional[plt.Axes]:
        """
        Returns the next available subplot Axes object.

        Returns:
            The next available subplot Axes object.

        Raises:
            IndexError: If no more subplots are available.
        """

        if self.current_iteration_index < self.n_plots:
            ax = self.axes[self.current_iteration_index]
            self.current_iteration_index += 1
            return ax
        logger.warning("No more subplots available")
        return None

    def __getitem__(self, index: int) -> plt.Axes:
        """
        Returns the subplot Axes object at the given index.

        Args:
            index: The index of the subplot Axes object to return.

        Returns:
            The subplot Axes object at the given index.

        Raises:
            IndexError: If the index is out of range.
        """

        if index < self.n_plots:
            return self.axes[index]

        raise IndexError("Index out of range")

    def __iter__(self) -> typing.Iterator[plt.Axes]:
        """
        Returns an iterator over the subplot Axes objects.

        Returns:
            An iterator over the subplot Axes objects.
        """
        return iter(self.axes)


def image_show(
    image: np.ndarray,
    ax: typing.Optional[plt.Axes] = None,
    cmap: str = "gray",
    show_grid: bool = False,
    hide_ticks: bool = True,
    **kwargs,
) -> plt.Axes:
    """
    Displays an image on the given Matplotlib Axes.

    Parameters:
        image: The image to display.
        ax: The Axes on which to display the image. If None, uses the current Axes.
        cmap: The colormap to use. Default is 'gray'.
        show_grid: Whether to display a grid. Default is False.
        hide_ticks: Whether to hide axis ticks and labels. Default is True.
        **kwargs: Additional keyword arguments to pass to ax.imshow().

    Returns:
        The Axes with the displayed image.
    """

    if ax is None:
        ax = plt.gca()

    ax.imshow(image, cmap=cmap, **kwargs)

    if not show_grid:
        ax.grid(False)

    if hide_ticks:
        ax.tick_params(axis="both", which="both", bottom=False, left=False, labelbottom=False, labelleft=False)

    return ax
