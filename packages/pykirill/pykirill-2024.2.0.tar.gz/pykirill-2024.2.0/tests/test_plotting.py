import sys
import unittest.mock

import matplotlib
import numpy as np
import pytest
import seaborn as sns
from matplotlib import pyplot as plt

from pykirill.plotting import SubplotsManager, setup


class TestSetup:
    def test_setup_seaborn_context(self):
        setup()
        # Retrieve the current context to check its properties
        current_context = sns.plotting_context()

        # Check specific properties to ensure the context is set to "notebook"
        assert current_context["font.size"] == 12, "Font size should be 12 for 'notebook' context"
        assert current_context["axes.titlesize"] == 12, "Axes title size should be 12 for 'notebook' context"

    def test_setup_seaborn_palette(self):
        setup()
        # Retrieve the current palette to check its colors
        current_palette = sns.color_palette()
        expected_colorblind = sns.color_palette("colorblind")

        # Compare the current palette with the expected "colorblind" palette
        assert all(
            [a == b for a, b in zip(current_palette, expected_colorblind)]
        ), "Palette should be 'colorblind', but it's not set correctly"

    @unittest.mock.patch.dict(sys.modules, {"IPython": None})
    def test_setup_without_ipython(self):
        # Simulate IPython not being present by returning None
        with unittest.mock.patch("logging.Logger.info") as mock_info:
            setup()
            mock_info.assert_any_call("IPython is not installed, IPython-specific configurations are skipped.")

    @unittest.mock.patch("IPython.get_ipython")
    def test_setup_with_ipython_not_running(self, mock_get_ipython):
        # Simulate running in a non-IPython environment
        mock_get_ipython.return_value = None
        with unittest.mock.patch("logging.Logger.info") as mock_info:
            setup()
            mock_info.assert_any_call(
                "Not running in an IPython environment. IPython-specific configurations are skipped."
            )

    @unittest.mock.patch("IPython.get_ipython")
    def test_setup_with_ipython_running(self, mock_get_ipython):
        # Simulate running in an IPython environment
        mock_ipy_instance = unittest.mock.Mock()
        mock_get_ipython.return_value = mock_ipy_instance
        setup()
        mock_ipy_instance.run_line_magic.assert_any_call("matplotlib", "inline")
        mock_ipy_instance.run_line_magic.assert_any_call("config", "InlineBackend.figure_format = 'retina'")

    def test_matplotlib_and_seaborn_configurations(self):
        setup()
        assert plt.rcParams["image.cmap"] == "viridis", "Matplotlib colormap should be 'viridis'"
        assert plt.rcParams["figure.autolayout"], "Matplotlib autolayout should be True"
        current_style = sns.axes_style()
        assert current_style["axes.grid"], "Seaborn grid should be on"

    def test_font_configuration(self):
        setup()
        arial_available = any("Arial" in font.name for font in matplotlib.font_manager.fontManager.ttflist)
        if arial_available:
            assert plt.rcParams["font.family"] == ["Arial"], "Font should be set to Arial"
        else:
            assert plt.rcParams["font.family"] == ["sans-serif"], "Font should be set to sans-serif"


class TestSubplotsManager:
    def test_initialize_with_single_dimension(self):
        n_plots = 6
        manager = SubplotsManager(n_plots, None)
        assert manager.n_rows == 2
        assert manager.n_columns == 3
        assert manager.n_plots == 6

    def test_initialize_with_tuple_dimensions(self):
        manager = SubplotsManager((3, 4), None)
        assert manager.n_rows == 3
        assert manager.n_columns == 4
        assert manager.n_plots == 12

    def test_figure_size_calculation(self):
        manager = SubplotsManager(4, None)
        expected_figure_size = (
            manager.COLUMNS_SCALING_FACTOR * manager.n_columns,
            manager.ROWS_SCALING_FACTOR * manager.n_rows,
        )
        assert manager.figure_size == expected_figure_size

    def test_custom_figure_size(self):
        custom_size = (15, 10)
        manager = SubplotsManager(4, custom_size)
        assert manager.figure_size == custom_size

    def test_create_subplots(self):
        manager = SubplotsManager(4, None)
        assert isinstance(manager.figure, plt.Figure)
        assert isinstance(manager.axes, np.ndarray)
        assert len(manager.axes) == 4

    def test_show_method(self):
        manager = SubplotsManager(4, None)
        with unittest.mock.patch.object(plt, "show") as mock_show:
            manager.show()
            mock_show.assert_called_once()

    def test_nextax_method(self):
        manager = SubplotsManager(4, None)
        for _ in range(4):
            ax = manager.nextax()
            assert isinstance(ax, plt.Axes)

        with unittest.mock.patch("logging.Logger.warning") as mock_warning:
            manager.nextax()
            mock_warning.assert_any_call("No more subplots available")

    def test_getitem_method(self):
        manager = SubplotsManager(4, None)
        ax = manager[2]
        assert isinstance(ax, plt.Axes)
        with pytest.raises(IndexError):
            manager[5]

    def test_iter_method(self):
        manager = SubplotsManager(4, None)
        axes = list(manager)
        assert len(axes) == 4
        assert all(isinstance(ax, plt.Axes) for ax in axes)

    def test_maximum_dimensions_in_one_row(self):
        maximum_dimensions = SubplotsManager.MAXIMUM_DIMENSIONS_IN_ONE_ROW
        manager = SubplotsManager(maximum_dimensions, None)
        assert manager.n_rows == 1
        assert manager.n_columns == maximum_dimensions

    def test_invalid_dimensions(self):
        with pytest.raises(ValueError):
            SubplotsManager("invalid", None)
