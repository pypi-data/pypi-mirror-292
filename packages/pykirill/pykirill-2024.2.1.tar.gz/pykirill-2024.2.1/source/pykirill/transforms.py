"""
Data transformation functions
"""

import typing

import numpy as np
import pandas as pd
import scipy.stats
import sklearn.decomposition
from numpy import typing as npt


def log_scale(x: npt.NDArray) -> npt.NDArray:
    """
    Applies a logarithmic transformation to the input array and then scales it.

    Args:
        x: Input array to be log-transformed and scaled.

    Returns:
        Log-transformed and scaled array.

    Usage:
        ```python
        # For NumPy arrays
        x = np.array([1, 2, 3, 4], dtype=np.float32)
        log_scaled_x = transforms.log_scale(x)

        # For Pandas DataFrames
        log_scaled_df = df.apply(transforms.log_scale)
        ```
    """

    epsilon = np.finfo(x.dtype).eps
    log_x = np.log(x + epsilon, dtype=x.dtype)
    return scipy.stats.zscore(log_x, nan_policy="omit")


class PrincipalComponentAnalysisResult(typing.NamedTuple):
    """
    A named tuple to store the results of Principal Component Analysis (PCA).

    Attributes:
        pca: The PCA object used to perform the analysis.
        scores: A DataFrame containing the principal component scores for each observation.
        loadings: A DataFrame containing the loadings for each variable in each principal component.
        cumulative_explained_variance: A Series containing the cumulative explained variance for each principal component.
        n_components: The number of principal components used in the analysis.
        names: A list of names for each principal component.

    Usage:
        ```python
        for pc, loading in pca.loadings.items():
            plt.hist(loading)
            plt.title(f"Loadings for {pc}")
            plt.xlabel("Loading value")
            plt.ylabel("Frequency")
            plt.show()
        ```
    """

    pca: sklearn.decomposition.PCA
    scores: pd.DataFrame
    loadings: pd.DataFrame
    cumulative_explained_variance: pd.Series
    n_components: int
    names: list[str]

    def __repr__(self):
        explained_variance = self.cumulative_explained_variance.iloc[-1]
        scores_shape = self.scores.shape
        loadings_shape = self.loadings.shape

        return (
            f"{self.__class__.__name__} (\n"
            f"\tN components: {self.n_components}\n"
            f"\tExplained variance: {explained_variance:.2f}\n"
            f"\tScores shape: {scores_shape}\n"
            f"\tLoadings shape: {loadings_shape}\n"
            ")"
        )


def principal_component_analysis(
    data: pd.DataFrame,
    n_components: typing.Optional[int] = None,
    pca_object: typing.Optional[sklearn.decomposition.PCA] = None,
) -> PrincipalComponentAnalysisResult:
    """
    Performs Principal Component Analysis (PCA) on the given data.

    Args:
        data: The input data to perform PCA on.
        n_components: The number of principal components to calculate. If None, all components are calculated.
        pca_object: An optional pre-fitted PCA object. If None, a new PCA object is created and fitted.

    Returns:
        A named tuple containing PCA results

    Usage:
        ```python
        pca = transforms.principal_component_analysis(
            data, n_components=3
        )
        for pc, score in pca.scores.items():
            print(f"{pc}:\t{score.mean():2g}")
        ```
    """

    if pca_object is None:
        pca_object = sklearn.decomposition.PCA(n_components=n_components).fit(data)

    if n_components is None:
        n_components = pca_object.n_components_

    scores_array = pca_object.transform(data)

    components_names = [f"PC{i}" for i in range(1, n_components + 1)]
    scores = pd.DataFrame(scores_array, columns=components_names, index=data.index)
    loadings = pd.DataFrame(pca_object.components_.T, index=data.columns, columns=components_names)
    cumulative_explained_variance = pd.Series(
        pca_object.explained_variance_ratio_, index=components_names, name="Cumulative explained variance"
    ).cumsum()

    return PrincipalComponentAnalysisResult(
        pca=pca_object,
        scores=scores,
        loadings=loadings,
        cumulative_explained_variance=cumulative_explained_variance,
        n_components=pca_object.n_components_,
        names=components_names,
    )
