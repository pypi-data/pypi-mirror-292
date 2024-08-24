from setuptools import setup, find_packages

setup(
    name = 'DesmoothForecaster',
    version = '0.1',
    packages = find_packages(),
    install_requires = ['numpy', 'pandas', 'statsmodels', 'scipy', 'matplotlib', 'seaborn'],
)