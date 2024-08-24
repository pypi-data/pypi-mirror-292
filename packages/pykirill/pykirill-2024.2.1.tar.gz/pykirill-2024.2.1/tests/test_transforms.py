import numpy as np
import pandas as pd
import pytest
from pykirill.transforms import PrincipalComponentAnalysisResult, log_scale, principal_component_analysis
from sklearn.decomposition import PCA


class TestLogScale:
    def test_positive_values(self):
        # Only positive values for log_scale
        x = np.array([1, 2, 3, 4], dtype=np.float32)
        log_scaled_x = log_scale(x)

        expected = np.array([-1.526072, -0.19470063, 0.5841019, 1.1366711], dtype=np.float32)

        assert np.all(np.isfinite(log_scaled_x)), "Result contains NaN or inf"

        np.testing.assert_array_almost_equal(log_scaled_x, expected, err_msg="Incorrect result")

        np.testing.assert_array_almost_equal(log_scaled_x.mean(), 0.0, err_msg="Mean is not zero")
        np.testing.assert_array_almost_equal(log_scaled_x.std(), 1.0, err_msg="Standard deviation is not one")

    def test_with_nan(self):
        # Only positive values for log_scale
        x = np.array([np.nan, 2, 3, 4, 5, 6], dtype=np.float32)
        log_scaled_x = log_scale(x)
        # Since exact values are hard to predict due to log, we check if result is finite
        expected = np.array(
            [np.nan, -1.6050358, -0.5599373, 0.1815718, 0.75673103, 1.2266703],
            dtype=np.float32,
        )

        assert np.sum(np.isfinite(log_scaled_x)) > 1, "Result contains more then one NaN or inf"

        np.testing.assert_array_almost_equal(log_scaled_x, expected, err_msg="Incorrect result")

        np.testing.assert_array_almost_equal(np.nanmean(log_scaled_x), 0.0, err_msg="Mean is not zero")
        np.testing.assert_array_almost_equal(np.nanstd(log_scaled_x), 1.0, err_msg="Standard deviation is not one")

    def test_with_zero_elements(self):
        # Input contains zero, should handle gracefully without errors
        x = np.array([0, 0, 1, 2, 3], dtype=np.float32)
        log_scaled_x = log_scale(x)

        assert np.all(np.isfinite(log_scaled_x))

    @pytest.mark.filterwarnings("ignore:Degrees of freedom <= 0 for slice")
    @pytest.mark.filterwarnings("ignore:Mean of empty slice")
    @pytest.mark.filterwarnings("ignore:invalid value encountered in log")
    def test_with_negative(self):
        # Input contains negative values, should result in NaNs or infs
        x = np.array([-1, -2, -3, -4], dtype=np.float32)
        result = log_scale(x)
        assert np.all(np.isnan(result) | np.isinf(result))


class TestPrincipalComponentAnalysis:
    @pytest.fixture
    def example_data(self):
        np.random.seed(0)
        return pd.DataFrame(np.random.rand(100, 5), columns=[f"Feature_{i}" for i in range(1, 6)])

    def test_pca_result_structure(self, example_data):
        """
        Test that the principal_component_analysis function returns a PrincipalComponentAnalysisResult object with the correct structure.
        """
        result = principal_component_analysis(example_data, n_components=3)

        assert isinstance(result, PrincipalComponentAnalysisResult)
        assert isinstance(result.pca, PCA)
        assert isinstance(result.scores, pd.DataFrame)
        assert isinstance(result.loadings, pd.DataFrame)
        assert isinstance(result.cumulative_explained_variance, pd.Series)
        assert isinstance(result.n_components, int)
        assert isinstance(result.names, list)

    def test_pca_scores_shape(self, example_data):
        """
        Test that the scores DataFrame has the correct shape after PCA.
        """
        n_components = 3
        result = principal_component_analysis(example_data, n_components=n_components)

        assert result.scores.shape == (example_data.shape[0], n_components)

    def test_pca_loadings_shape(self, example_data):
        """
        Test that the loadings DataFrame has the correct shape after PCA.
        """
        n_components = 3
        result = principal_component_analysis(example_data, n_components=n_components)

        assert result.loadings.shape == (example_data.shape[1], n_components)

    def test_cumulative_explained_variance(self, example_data):
        """
        Test that the cumulative explained variance is correctly calculated.
        """
        result = principal_component_analysis(example_data, n_components=3)
        assert np.all(result.cumulative_explained_variance.diff().iloc[1:] > 0)

    def test_custom_pca_object(self, example_data):
        """
        Test that passing a custom PCA object works correctly.
        """
        custom_pca = PCA(n_components=2).fit(example_data)
        result = principal_component_analysis(example_data, pca_object=custom_pca)

        assert result.pca is custom_pca
        assert result.n_components == 2

    def test_repr_output(self, example_data):
        """
        Test the __repr__ method to ensure the output string contains the expected information.
        """
        result = principal_component_analysis(example_data, n_components=3)
        repr_output = repr(result)

        assert "PrincipalComponentAnalysisResult" in repr_output
        assert f"N components: {result.n_components}" in repr_output
        assert f"Explained variance: {result.cumulative_explained_variance.iloc[-1]:.2f}" in repr_output
        assert f"Scores shape: {result.scores.shape}" in repr_output
        assert f"Loadings shape: {result.loadings.shape}" in repr_output

    def test_default_n_components(self, example_data):
        """
        Test that the function correctly sets n_components to the number of features if not provided.
        """
        result = principal_component_analysis(example_data)

        assert result.n_components == example_data.shape[1]
        assert len(result.names) == example_data.shape[1]
