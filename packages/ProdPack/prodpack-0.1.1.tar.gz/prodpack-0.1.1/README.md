# ProdPack: An Efficiency and Productivity Analysis Package

ProdPack is a Python package designed for Efficiency and Productivity Analysis. Its comprehensive toolset allows for efficient handling of various productivity index estimates, including those that account for undesirable outputs (e.g., total factor productivity, TFP).

## Installation

Install the package by `pip`,

```sh
pip install ProdPack
```
Or install the package by `conda`,
```sh
conda install ProdPack
```

## Usage

A brief example is provided below. For more information, please refer to the [documentation]() and [example notebooks]().

```python
# import the module
import pandas as pd
from ProdPack.model import ProdNP
from DEAPack.utilities import load_example_data

# load the example dataset
data = load_example_data()

# initilise a nonparametric model
model = ProdNP()

# specify the model
model.DMUs = data['region']
model.x_vars = data[['K', 'L']]
model.y_vars = data[['Y']]
model.b_vars = data[['CO2']]
model.time = data['year']
model.g_x = model.x_vars*0
model.ref_type = 'Sequential'

# solve the model
model.solve()

# check the results
data['prod_ch'] = model.prod_ch
data['eff_ch'] = model.eff_ch
data['te_ch'] = model.te_ch
print(data)
# the results are combind into the data set
```

## Communication

You're very welcome to contribute to this package. We appreciate any efforts to improve this package. You can help by adding new features, reporting bugs, or extending the documentation and usage examples. Please contact us if you have any ideas.

- [Pull requests](https://github.com/daopingw/ProdPack/pulls) for pull requests.
- [Issues](https://github.com/daopingw/ProdPack/issues) for bug reports.
