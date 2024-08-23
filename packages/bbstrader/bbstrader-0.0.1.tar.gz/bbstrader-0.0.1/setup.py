from setuptools import setup
import sys

if sys.version_info < (3,9):
    sys.exit("Only Python 3.9 and greater is supported") 

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Simplified Investment & Trading Toolkit'

# Setting up
setup(
    name="bbstrader",
    version=VERSION,
    author='Bertin Balouki SIMYELI',
    url='https://github.com/bbalouki/bbstrade',
    license='The MIT License (MIT)',
    author_email='<bbalouki@outlook.com>',
    maintainer='Bertin Balouki SIMYELI',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=[
        "bbstrader", 
        "bbstrader.btengine", 
        "bbstrader.metatrader",
        "bbstrader.models",
        "bbstrader.trading"
    ],
    install_requires=[
        "pandas",
        "numpy==1.26.4",
        "yfinance",
        "scipy",
        "hmmlearn",
        "pmdarima",
        "arch",
        "hurst",
        "seaborn",
        "statsmodels",
        "matplotlib",
        "filterpy",
        "pytest",
        "sphinx",
        "sphinx-rtd-theme",
        "CurrencyConverter",
        "Metatrader5"
        ],
    keywords=[
        "Finance",
        "Toolkit",
        "Financial",
        "Analysis",
        "Fundamental",
        "Quantitative",
        "Database",
        "Equities",
        "Currencies",
        "Economics",
        "ETFs",
        "Funds",
        "Indices",
        "Moneymarkets",
        "Commodities",
        "Futures",
        "CFDs",
        "Derivatives",
        "Trading",
        "Investing",
        "Portfolio",
        "Optimization",
        "Performance",
        ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ]
)