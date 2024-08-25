
# easyformer

A Python package for creating machine learning pipelines that standardize numerical columns and encode categorical columns using `LabelEncoder` or `OneHotEncoder` based on the number of unique values.

## Installation

You can install the package from PyPI using pip:

```bash
pip install easyformer
```

## Usage

### 1. Import the Package

```python
from easyformer import create_pipeline
import pandas as pd
```

### 2. Load Your Data

```python
# Example: Load a CSV file into a pandas DataFrame
data = pd.read_csv('your_data.csv')
```

### 3. Create the Pipeline

```python
pipeline = create_pipeline(data)
```

### 4. Fit and Transform Your Data

```python
# Fit the pipeline to your data and transform it
transformed_data = pipeline.fit_transform(data)
```

### 5. (Optional) Convert Transformed Data Back to a DataFrame

```python
# If you need the transformed data as a DataFrame
transformed_df = pd.DataFrame(transformed_data, columns=pipeline.named_steps['preprocessor'].get_feature_names_out())
print(transformed_df.head())
```

### Example

Here’s a full example that puts everything together:

```python
from easyformer import create_pipeline
import pandas as pd

# Load your data
data = pd.read_csv('your_data.csv')

# Create the pipeline
pipeline = create_pipeline(data)

# Fit and transform your data
transformed_data = pipeline.fit_transform(data)

# Optionally convert the transformed data back to a DataFrame
transformed_df = pd.DataFrame(transformed_data, columns=pipeline.named_steps['preprocessor'].get_feature_names_out())
print(transformed_df.head())
```

## Description

The `easyformer` package automates the preprocessing steps for machine learning pipelines by:

- **Standardizing Numerical Columns:** All numerical columns are scaled using `StandardScaler`.
- **Encoding Categorical Columns:** 
  - Columns with only two unique values are encoded using `LabelEncoder`.
  - Columns with more than two unique values are one-hot encoded using `OneHotEncoder`.
- **Removing Original Categorical Columns:** The original categorical columns are dropped after encoding.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

If you would like to contribute to this package, please submit a pull request or open an issue on the [GitHub repository](https://github.com/gaharivatsa/easyformer).
