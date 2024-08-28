#!/usr/bin/env python
# coding: utf-8

# In[1]:


from setuptools import setup, find_packages

setup(
    name="datasetchecker",
    version="0.1.0",
    description="A library for checking datasets for common errors like missing values, duplicates, data type mismatches, and outliers.",
    author="Muhammad Ammar Jamshed",
    author_email="ammarjamshed123@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


# In[ ]:




