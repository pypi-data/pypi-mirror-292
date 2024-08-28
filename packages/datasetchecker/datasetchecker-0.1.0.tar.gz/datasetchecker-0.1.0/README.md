dataset_checker

is a Python library designed to help you quickly identify and resolve common errors in datasets. Whether you're working on data analysis, machine learning projects, or data preprocessing, this library can help you ensure your data is clean and ready for use.

FEATURES
- Missing Values Detection: Automatically identifies columns with missing values in your dataset.
- Duplicate Rows Detection: Detects and counts duplicate rows that might skew your data analysis.
- Data Type Mismatch Detection: Finds columns where data types are inconsistent, such as strings in numeric columns.
- Outlier Detection: Identifies outliers in numeric data using standard deviation, helping you to spot potential data anomalies.

INSTALLATION
You can install the dataset_checker library using pip. First, ensure you have Python 3.6 or later installed, then run:
pip install dataset_checker

USAGE
Here’s a basic example of how to use the dataset_checker library in your project:

import pandas as pd
from dataset_checker.error_checker import check_for_errors

# Load your dataset
df = pd.read_csv("your_dataset.csv")

# Check for errors in the dataset
errors = check_for_errors(df)

# Display the errors found
for i, error in enumerate(errors):
    print(f"{i+1}. {error}")


EXAMPLE OUTPUT
1. Missing Values:
   ColumnA    5
   ColumnB    2

2. Duplicate Rows: 10

3. Data Type Mismatch in Column 'ColumnC': Contains string values in numeric column

4. Outliers detected in Column 'ColumnD':
   34     100.0
   67     -50.0



YOU FEEL LIKE `Contributing`
Contributions are welcome! If you’d like to improve this library or add new features, feel free to fork the repository and submit a pull request. Please ensure your contributions are well-documented and tested.


AUTHOR
Muhammad Ammar Jamshed - GitHub Profile: https://github.com/AmmarJamshed

ACKNOWLEDGMENTS
Special thanks to the open-source community for providing the tools and resources that made this project possible. Not to mention OpenAI for developing GPTs allowing me to research and test my code much faster.