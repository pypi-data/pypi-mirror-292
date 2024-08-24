# CEEMDAN-LSTM-GradientBoosting

A state-of-the-art time series forecasting model combining CEEMDAN decomposition, LSTM neural networks, and Gradient Boosting.

## Installation

You can install the package using pip:

```
pip install ceemdan_seglstm_gradient_boost
```

## Usage

Here's a basic example of how to use the package:

```python
from ceemdan_seglstm_gradient_boost import Model, Dataset_ETT_hour

# Load your data
dataset = Dataset_ETT_hour(root_path='path/to/data', flag='train', size=[12, 12, 12], 
                           features='M', data_path='your_data.csv', 
                           target='your_target_column', max_imfs=8)

# Initialize the model
model = Model(your_config)

# Train the model
# ... (add training code here)

# Make predictions
# ... (add prediction code here)
```

## Dependencies

- torch
- numpy
- pandas
- matplotlib
- scikit-learn
- joblib
- PyEMD

## License

This project is licensed under the MIT License.