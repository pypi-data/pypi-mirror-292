from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name = 'DesmoothForecaster',
    version = '0.3',
    packages = find_packages(),
    install_requires = ['numpy', 'pandas', 'statsmodels', 'tensorflow', 'scikit-learn', 'seaborn', 'matplotlib'],
    long_description=long_description,
    long_description_content_type='text/markdown',
)