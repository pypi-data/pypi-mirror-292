#!/usr/bin/env python
# coding: utf-8

# In[1]:


# dataset_checker/error_checker.py

import pandas as pd

def check_for_errors(df):
    errors = []

    # Check for missing values
    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]
    if not missing_values.empty:
        errors.append(f"Missing Values:\n{missing_values}\n")

    # Check for duplicate rows
    duplicate_rows = df.duplicated().sum()
    if duplicate_rows > 0:
        errors.append(f"Duplicate Rows: {duplicate_rows}\n")

    # Check for data type mismatches (e.g., strings in numeric columns)
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].apply(lambda x: isinstance(x, str)).sum() > 0:
                errors.append(f"Data Type Mismatch in Column '{col}': Contains string values in numeric column\n")

    # Check for outliers in numeric columns
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        outliers = df[col][((df[col] - df[col].mean()) / df[col].std()).abs() > 3]
        if not outliers.empty:
            errors.append(f"Outliers detected in Column '{col}':\n{outliers}\n")

    if not errors:
        errors.append("No errors detected.")
        
    return pd.Series(errors)


# In[2]:


df = pd.read_csv(r'C:\Users\User\Downloads\edjjke.csv')
df


# In[3]:


check_for_errors(df)


# In[ ]:




