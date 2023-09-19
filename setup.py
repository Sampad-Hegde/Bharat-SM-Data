from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="Bharat_sm_data",
    version="1.0.0",
    description="Bharat (India) Stock Market Data Fetch Library for all kind of data, Derivatives, Equity "
                "(both Technical and Fundamentals), Commodities, Currencies from NSE, MoneyControl and "
                "Tickertape websites",
    package_dir={"": "Bharat_sm_data"},
    packages=find_packages(where="Bharat_sm_data"),
    exclude_package_data={
        '': ['Base/*'],  # Exclude specific file types from the root directory
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    author="Sampad Hegde",
    author_email="me@sampadhegde.in",
    license="apache-2",
    classifiers=[
        "License :: OSI Approved :: Apache-2",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests >= 2.31.0',
        'pandas >= 2.0.3',
        'pydash >= 7.0.6',
        'beautifulsoup4 >= 4.12.2',
        'numpy >= 1.25.2'
    ],
    extras_require={
        "dev": ["twine>=4.0.2"],
    },
    python_requires=">=3.8",
)