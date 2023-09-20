<div align="center">
<h1 align="center">
<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" />
<br>Bharat-SM-Data
</h1>
<h3>◦ Bharat-SM-Data: Empowering India's Progress</h3>
<h3>◦ Developed with the software and tools listed below.</h3>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/pandas-150458.svg?style&logo=pandas&logoColor=white" alt="pandas" />
</p>
</div>

---

## 📒 Table of Contents
- [📒 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [⚙️ Features](#-features)
- [📂 Project Structure](#project-structure)
- [🧩 Modules](#modules)
- [🚀 Getting Started](#-getting-started)
- [🗺 Roadmap](#-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👏 Acknowledgments](#-acknowledgments)

---


## 📍 Overview

The project is a comprehensive library written in Python that provides functionalities for fetching various types of stock market data from Indian websites such as NSE, MoneyControl, and Tickertape. It supports derivatives, equity (both technical and fundamentals), commodities, and currencies. The library offers easy access to market data, including historical and current values, option chain data, trade information, and more. Its purpose is to simplify the retrieval of stock market data and enhance the analysis and decision-making process for traders and investors.

---

## ⚙️ Features

| Feature                | Description                                                                                                                                                                                       |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **⚙️ Architecture**     | The codebase follows a modular architecture with separate directories for different aspects of stock market data retrieval (Fundamentals, Technical, Derivatives).                                |
| **📖 Documentation**    | The codebase includes documentation for each module and class, providing detailed explanations of methods and functionalities.                                                                     |
| **🔗 Dependencies**     | External libraries like Pandas, Pydash, and HTTPStatus are used for data manipulation, utility methods, and HTTP handling respectively. The codebase relies on APIs from NSE, MoneyControl, and Tickertape.  |
| **🧩 Modularity**       | The codebase is organized into smaller and interchangeable components, allowing users to fetch stock market data from NSE, MoneyControl, and Tickertape using different modules in a modular manner. |
| **✔️ Testing**          | The testing strategy and tools used in the codebase are not explicitly mentioned or evident from the provided information.                                                                       |
| **⚡️ Performance**      | The codebase includes a custom session class and implements pruning to improve efficiency, reduce memory usage, and enhance overall performance.                                                   |
| **🔐 Security**         | The measures taken by the system to protect data and maintain functionality are not explicitly mentioned or evident from the provided information.                                                |
| **🔀 Version Control**  | The codebase is hosted on GitHub, indicating the use of Git for version control.                                                                                                                   |
| **🔌 Integrations**     | The system integrates with external APIs like NSE, MoneyControl, and Tickertape to fetch stock market data from different sources.                                                                 |
| **📶 Scalability**      | The codebase's scalability is not explicitly discussed or evident from the provided information. However, the modular architecture and the use of external APIs indicate potential scalability options.   |

---


## 📂 Project Structure




---

## 🧩 Modules

<details closed><summary>Root</summary>

| File                                                                                                                        | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ---                                                                                                                         | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| [MANIFEST.in](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/MANIFEST.in)                                     | The code implements a pruning function in a base class. It purposefully removes unnecessary elements to improve efficiency and reduce memory usage, enhancing the overall performance of the program.                                                                                                                                                                                                                                                                                           |
| [setup.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/setup.py)                                           | This code configures a package named "Bharat_sm_data" with various functionalities for fetching stock market data from NSE, MoneyControl, and Tickertape. It manages dependencies, provides package metadata, and sets package requirements.                                                                                                                                                                                                                                                    |
| [CustomRequest.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/Bharat_sm_data\Base\CustomRequest.py)       | The code provides a CustomSession class that creates a session object with retries, timeouts, and headers. It allows users to send HTTP requests, handle JSON responses, and retrieve data from APIs.                                                                                                                                                                                                                                                                                           |
| [NSEBase.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/Bharat_sm_data\Base\NSEBase.py)                   | The code implements a class to interact with the NSE (National Stock Exchange) API. It provides functionalities to retrieve market status, current value, historical data, and search for equities and derivatives. It uses Pandas for data manipulation and Pydash for utility methods.                                                                                                                                                                                                        |
| [PKG-INFO](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/Bharat_sm_data\Bharat_sm_data.egg-info\PKG-INFO)    | This code is a comprehensive library for fetching all types of stock market data from various Indian websites. It supports derivatives, equity (both technical and fundamentals), commodities, and currencies. It provides easy access to data from NSE, MoneyControl, and Tickertape websites. The code is written in Python and requires Python version 3.8 or later. The library is licensed under the Apache-2 license.                                                                     |
| [NSE.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/Bharat_sm_data\Derivatives\NSE.py)                    | The code provides a class for interacting with the NSE (National Stock Exchange) API. It includes methods for fetching option chain data, retrieving expiry dates, getting trade information for equity futures and options, retrieving index futures data, fetching currency and commodity futures data, and calculating put-call ratios. The code is well-documented and follows best practices.                                                                                              |
| [Sensibull.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/Bharat_sm_data\Derivatives\Sensibull.py)        | The code represents a class, "Sensibull", which interacts with the Sensibull API. It has methods to search for tokens, retrieve token details, and get options data with Greeks. The code is well-documented with detailed explanations for each method.                                                                                                                                                                                                                                        |
| [MoneyControl.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/Bharat_sm_data\Fundementals\MoneyControl.py) | HTTPStatus Exception: 400                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| [TickerTape.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/Bharat_sm_data\Fundementals\TickerTape.py)     | HTTPStatus Exception: 400                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| [NSE.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/Bharat_sm_data\Technical\NSE.py)                      | The code provides a class for interacting with the NSE API, allowing functions to retrieve important reports, equities data from indices, trade information, corporate disclosures, SME stocks, SGB data, ETF data, block deals, and India VIX data. It utilizes the pandas library for data manipulation.                                                                                                                                                                                      |
| [CustomRequest.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/build\lib\Base\CustomRequest.py)            | The code provides a CustomSession class that creates a session object with retries, timeouts, and headers for making HTTP requests. It includes methods for returning the session object and hitting an API to retrieve data based on a given URL and parameters. The code handles JSON decoding errors and exceptions when connecting to a URL.                                                                                                                                                |
| [NSEBase.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/build\lib\Base\NSEBase.py)                        | The code is a Python class that interacts with the NSE (National Stock Exchange) API. It provides functions to retrieve market status, current values, OHLC data, and search for equities and derivatives. The code utilizes libraries like pandas and pydash for efficient data manipulation.                                                                                                                                                                                                  |
| [NSE.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/build\lib\Derivatives\NSE.py)                         | This code defines a class called NSE that interacts with the NSE (National Stock Exchange) API. It provides various methods for fetching data related to stocks, futures, options, indices, currencies, and commodities. Some of the core functionalities include fetching option chain data, getting trade information for equity futures and options, retrieving data for index futures, currency futures, and commodity futures, and calculating the put-call ratio (PCR) for a given stock. |
| [Sensibull.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/build\lib\Derivatives\Sensibull.py)             | The code is a Python class that interacts with the Sensibull API. It provides functionalities to search for tokens, get token details, and retrieve options data with Greeks. It uses Pandas and Pydash libraries for data manipulation and extends a custom session class for API requests.                                                                                                                                                                                                    |
| [MoneyControl.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/build\lib\Fundementals\MoneyControl.py)      | HTTPStatus Exception: 400                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| [TickerTape.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/build\lib\Fundementals\TickerTape.py)          | HTTPStatus Exception: 400                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| [NSE.py](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/build\lib\Technical\NSE.py)                           | The code provides a class to interact with the NSE (National Stock Exchange) API, allowing users to retrieve data on important reports, equities, indices, trade information, corporate disclosures, SME stocks, SGB data, ETFs, block deals, and the India VIX. The code utilizes pandas for data manipulation and the MoneyControl class for fetching data on the India VIX.                                                                                                                  |
| [Derivatives.ipynb](https://github.com/Sampad-Hegde/Bharat-SM-Data.git/blob/main/examples\Derivatives.ipynb)                | HTTPStatus Exception: 400                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

</details>

---

## 🚀 Getting Started

### ✔️ Prerequisites

Before you begin, ensure that you have the following prerequisites installed:
> - `ℹ️ create a new python venv or use old one`
> - `ℹ️ pip install Bhart_sm_data`

### 📦 Installation

1. Clone the Bharat-SM-Data repository:
```sh
git clone https://github.com/Sampad-Hegde/Bharat-SM-Data.git
```

2. Change to the project directory:
```sh
cd Bharat-SM-Data
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```

### 🎮 Using Bharat-SM-Data

```sh
python main.py
```

### 🧪 Running Tests
```sh
pytest
```

---


## 🗺 Roadmap

> - [X] `ℹ️  Task 1: Implement X`
> - [ ] `ℹ️  Task 2: Refactor Y`
> - [ ] `ℹ️ ...`


---

## 🤝 Contributing

Contributions are always welcome! Please follow these steps:
1. Fork the project repository. This creates a copy of the project on your account that you can modify without affecting the original project.
2. Clone the forked repository to your local machine using a Git client like Git or GitHub Desktop.
3. Create a new branch with a descriptive name (e.g., `new-feature-branch` or `bugfix-issue-123`).
```sh
git checkout -b new-feature-branch
```
4. Make changes to the project's codebase.
5. Commit your changes to your local branch with a clear commit message that explains the changes you've made.
```sh
git commit -m 'Implemented new feature.'
```
6. Push your changes to your forked repository on GitHub using the following command
```sh
git push origin new-feature-branch
```
7. Create a new pull request to the original project repository. In the pull request, describe the changes you've made and why they're necessary.
The project maintainers will review your changes and provide feedback or merge them into the main branch.

---

## 📄 License

This project is licensed under the `ℹ️  INSERT-LICENSE-TYPE` License. See the [LICENSE](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-license-to-a-repository) file for additional info.

---

## 👏 Acknowledgments

> - `ℹ️  List any resources, contributors, inspiration, etc.`

---
