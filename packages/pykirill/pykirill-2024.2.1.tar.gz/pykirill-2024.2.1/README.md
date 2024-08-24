# 🐗 pykirill

[Documentation](https://kirilledition.github.io/pykirill/)

This is my personal Python package, `pykirill`, which includes a collection of utilities and functions that I frequently use during scientific exploration. This package is especially designed to be portable, making it suitable for environments like Google Colab where setup needs to be minimal.

## Installation

There are several ways to install `pykirill`

### PyPI

You can use regualar `pip install` from PyPI

```bash
pip install pykirill
```

### GitHub source

You can use pip to install directly from GitHub. This method ensures you always get the latest version. Also gives access to experimental features in development

```bash
pip install git+https://github.com/kirilledition/pykirill.git@main
```

### GitHub release

You also can use link to wheel from github releases

```bash
pip install https://github.com/kirilledition/pykirill/releases/download/2024.2.1/pykirill-2024.2.1-py3-none-any.whl
```

### GitHub Container Registry

And finally package is also runnable as docker container from GitHub Container Registry

```bash
docker run --rm -it ghcr.io/kirilledition/pykirill:2024.2.1
```

## Usage

You can have a look at showcase jupyter notebooks, that shows primitive examples of how to use `pykirill`: [showcase.ipynb](https://kirilledition.github.io/pykirill/showcase/)

### Transforms
```python
from pykirill import transforms

scaled_data = data.apply(transforms.log_scale)
pca = transforms.principal_component_analysis(
  scaled_data, n_components=3
)
```

### Plotting
```python
from pykirill import plotting
plotting.setup()

axm = plotting.SubplotsManager(pca.n_components)

for pc, score in pca.scores.items():
    ax = axm.nextax()

    ax.set_title(pc)
    ax.set_ylabel("PC score")
    ax.set_xlabel("species")

    sns.boxplot(x=target, y=score, ax=ax)

axm.show()
```

## License

`pykirill` is open-sourced under the MIT license. The details can be found in the [LICENSE.md](https://github.com/kirilledition/pykirill/blob/main/LICENSE.md) file.