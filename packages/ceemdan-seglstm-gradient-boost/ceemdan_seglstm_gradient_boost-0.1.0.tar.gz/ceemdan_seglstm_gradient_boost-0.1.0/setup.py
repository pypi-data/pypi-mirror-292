from setuptools import setup, find_packages

setup(
    name="ceemdan_seglstm_gradient_boost",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'torch',
        'numpy',
        'pandas',
        'matplotlib',
        'scikit-learn',
        'joblib',
        'PyEMD',
    ],
    author="manawi kahie",
    author_email="manawi07@icloud.com",
    description="CEEMDAN-LSTM-GradientBoosting model for state-of-the-art time series forecasting",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ese-msc-2023/irp-mk1923/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)