from setuptools import find_packages, setup


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="Bharat_sm_data",
    version="4.0.1",
    description="Bharat SM Data stands for Bharat(India) Stock Market Data."
                "\nIt is a Bharat (India) Stock Market Data Fetch Library for all kind of data, Derivatives, Equity "
                "(both Technical and Fundamentals), Commodities, Currencies from NSE, BSE, MoneyControl and "
                "Tickertape websites",
    package_dir={"": "Bharat_sm_data"},
    packages=find_packages(where="Bharat_sm_data"),
    exclude_package_data={
        '': ['Base/*'],  # Exclude specific file types from the root directory
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sampad-Hegde/Bharat-SM-Data",
    author="Sampad Hegde",
    author_email="me@sampadhegde.in",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Brotli>=1.0.0',
        'requests>=2.31.0',
        'pandas>=2.0.3',
        'pydash>=7.0.6',
        'beautifulsoup4>=4.12.2',
        'numpy>=1.25.2',
        'html5lib>=1.1',
        'lxml>=4.9.3'
    ],

    extras_require={
        "dev": ["twine>=4.0.2"],
    },
    python_requires=">=3.7",
    project_urls={
        "Documentation": "https://bharat-sm-data.readthedocs.io/en/latest/"
    },
)