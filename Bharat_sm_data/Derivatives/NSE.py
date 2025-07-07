from datetime import datetime

import pandas as pd
import pydash as _
from bs4 import BeautifulSoup

from Base import NSEBase


class NSE(NSEBase):
    """
        A class to interact with NSE (National Stock Exchange) API.

        Attributes:
            valid_pcr_fields : list of valid fields for put-call ratio calculation

        Methods:
            __init__ : Initialize the NSE class
            get_option_chain : Get the option chain for a given ticker
            get_raw_option_chain : Get the raw option chain data for a given ticker
            get_options_expiry : Get the next expiry date for a given ticker
            get_all_derivatives_enabled_stocks : Get the list of equities available for derivatives trading
            get_equity_future_trade_info : Get the trade information of active future contracts for a given ticker
            get_equity_options_trade_info : Get the trade information of equity options for a given ticker
            _mapped_index_ticker_for_futures : Get the mapped index ticker for index futures
            get_index_futures_data : Get the data for index futures of a given index or ticker
            get_currency_futures : Get the data for currency futures
            get_commodity_futures : Get the data for commodity futures
            get_pcr : Get the put-call ratio for a given ticker and expiry date
    """

    def __init__(self) -> None:
        """
            The __init__ function is called when the class is instantiated.
            It sets up the session and headers for all subsequent requests.

            :param self: Represent the instance of the class

            :return: Nothing
        """

        super().__init__()
        self.headers['Referer'] = 'https://www.nseindia.com/option-chain'
        self.hit_and_get_data(f'{self._base_url}/option-chain')
        self.valid_pcr_fields = ['oi', 'volume']

    # ----------------------------------------------------------------------------------------------------------------
    # Utility Functions

    def get_option_chain(self, ticker: str, expiry: datetime, is_index: bool = True) -> pd.DataFrame:
        """
            The get_option_chain function takes a ticker as input and returns the option chain for that ticker. The
            function uses the try_n_times_get_response function to get a response from NSE's API, which is then converted
            into a DataFrame using pd.json_normalize.

            :param self: Represent the instance of the class
            :param ticker: Specify the stock ticker for which we want to get the option chain its also called symbol in
            NSE
            :param is_index: (optional) Boolean value Specifies the given ticker is an index or not
            :param expiry: (optional) It takes the `expiry date` in the datetime format of the options contracts,
            default is very next expiry day

            :return: A dataframe with option chain
        """

        params = {'symbol': ticker, 'expiry': expiry.strftime('%d-%b-%Y')}
        url = f'{self._base_url}/api/option-chain-v3'

        if is_index:
            params['type'] = 'Indices'
        else:
            params['type'] = 'Equity'

        response = self.hit_and_get_data(url, params=params)
        df = pd.DataFrame(pd.json_normalize(_.get(response, 'records.data', {}), sep='_')).set_index('strikePrice')
        return df

    def get_raw_option_chain(self, ticker: str, expiry: datetime, is_index: bool = True) -> dict:
        """
            The get_option_chain function takes a ticker as input and returns the option chain for that ticker.
            The function uses the try_n_times_get_response function to get a response from NSE's API, which is
            then converted into a DataFrame using pd.json_normalize.

            :param is_index: Boolean value Specifies the given ticker is an index or not
            :param self: Represent the instance of the class
            :param ticker: Specify the stock ticker for which we want to get the option chain

            :return: A dataframe with option chain data
        """

        params = {'symbol': ticker, 'expiry': expiry.strftime('%d-%b-%Y')}
        url = f'{self._base_url}/api/option-chain-v3'

        if is_index:
            params['type'] = 'indices'
        else:
            params['type'] = 'Equity'

        response = self.hit_and_get_data(url, params=params)
        return response

    def get_options_expiry(self, ticker: str, is_index: bool = False) -> datetime:
        """
            The get_expiry function takes in a ticker and returns the next expiry date for that ticker.
            The function uses the NSE API to get all expiry dates for a given ticker, sorts them in ascending order,
            and then returns the nth element of this sorted list.

            :param self: Represent the instance of the class
            :param ticker: Specify the ticker / symbol for which we want to get the expiry date
            :param is_index: Boolean value Specifies the given ticker is an index or not

            :return: The very next expiry date
        """

        params = {'symbol': ticker}
        if is_index:
            url = f'{self._base_url}/api/option-chain-contract-info'
        else:
            url = f'{self._base_url}/api/option-chain-contract-info'
        response = self.hit_and_get_data(url, params=params)
        dates = sorted([datetime.strptime(date_str, "%d-%b-%Y") for date_str in
                        response.get('expiryDates', [])])
        return dates

    # ----------------------------------------------------------------------------------------------------------------_
    # Equity Futures
    def get_all_derivatives_enabled_stocks(self) -> list:
        """
            The get_all_derivatives_enabled_stocks provides the list of Equities available for derivative trading

            :param self: Represent the instance of the class

            :return: List of all Equities tickers / symbols for which derivative trading is allowed
        """

        response = self.hit_and_get_data(f'{self._base_url}/api/master-quote')
        return response

    def get_equity_future_trade_info(self, ticker: str) -> pd.DataFrame:
        """
            The get_equity_future_trade_info provides all active future contracts trade information including its price
            details

            :param self: Represent the instance of the class
            :param ticker: Specify the ticker / symbol for which we want to get the expiry date

            :return: A DataFrame of trade info data of Equity Future contracts
        """

        params = {'symbol': ticker}
        response = self.hit_and_get_data(f'{self._base_url}/api/quote-derivative', params=params)
        future_data = []
        for fno_data in response.get('stocks', []):
            if fno_data.get('metadata', {}).get('instrumentType') == 'Stock Futures':
                future_data.append(fno_data)

        df = pd.DataFrame(pd.json_normalize(future_data, sep='_'))
        df['ticker'] = response.get('info', {}).get('symbol', '')
        df['companyName'] = response.get('info', {}).get('companyName', '')
        df['industry'] = response.get('info', {}).get('industry', '')
        df['fut_timestamp'] = response.get('fut_timestamp', '')
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Equity Options

    def get_equity_options_trade_info(self, ticker: str) -> pd.DataFrame:
        """
            Gets equity options trade information for a given ticker.

            :param ticker: Ticker symbol of the equity options trade.

            :return: DataFrame containing the trade information.
        """

        params = {'symbol': ticker}
        response = self.hit_and_get_data(f'{self._base_url}/api/quote-derivative', params=params)
        future_data = []
        for fno_data in response.get('stocks', []):
            if fno_data.get('metadata', {}).get('instrumentType') == 'Stock Options':
                future_data.append(fno_data)

        df = pd.DataFrame(pd.json_normalize(future_data, sep='_'))
        df['ticker'] = response.get('info', {}).get('symbol', '')
        df['companyName'] = response.get('info', {}).get('companyName', '')
        df['industry'] = response.get('info', {}).get('industry', '')
        df['opt_timestamp'] = response.get('opt_timestamp', '')
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Index Futures
    def _mapped_index_ticker_for_futures(self) -> dict:
        """
            Mapped index ticker will give dict of available options with its corresponding ticker value

            :param self: Represent the instance of the class

            :return: A dict obj with all FUTURES mappings
        """

        response = self.session.get(f'{self._base_url}//market-data/equity-derivatives-watch',
                                    headers=self.headers)
        soup = BeautifulSoup(response.text, features="html5lib")
        all_derivative_options = soup.find_all('option', attrs={"rel": "derivative"})
        mapped_index_ticker = {}
        for i in all_derivative_options:
            mapped_index_ticker[i.get_text().lower()] = i['value']

        return mapped_index_ticker

    def get_index_futures_data(self, index_or_ticker: str) -> pd.DataFrame:
        """
            Fetches index futures data.

            :param self: Represent the instance of the class
            :param index_or_ticker: Name or ticker symbol of the index.

            :return: DataFrame containing the FUTURES data
        """

        index_or_ticker = index_or_ticker.lower()
        mapped_tickers = {}

        try:
            mapped_tickers = self._mapped_index_ticker_for_futures()
        except Exception as err:
            print(
                f'Exception in fetching mapped ticker for this index try to pass actual ticker in the next call,  '
                f'Exact error : {err}')

        if index_or_ticker in mapped_tickers.keys():
            ticker_to_used = mapped_tickers[index_or_ticker]
        else:
            ticker_to_used = index_or_ticker
        params = {'index': ticker_to_used}
        response = self.hit_and_get_data(f'{self._base_url}/api/liveEquity-derivatives', params=params)
        df = pd.DataFrame(response.get('data', []))
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Currency

    def get_currency_futures(self) -> pd.DataFrame:
        """
            Fetches currency futures data.

            :param self: Represent the instance of the class

            :return: DataFrame containing the currency futures data
        """

        params = {'index': 'live_market_currency', 'key': 'INR'}
        response = self.hit_and_get_data(
            f'{self._base_url}/api/liveCurrency-derivatives', params=params)
        df = pd.DataFrame(response.get('data', []))
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Commodity
    def get_commodity_futures(self) -> pd.DataFrame:
        """
            Fetches commodity futures data.

            :param self: Represent the instance of the class

            :return: Pd.DataFrame: DataFrame containing the currency futures data
        """
        response = self.hit_and_get_data(f'{self._base_url}/api/liveCommodity-derivatives')
        df = pd.DataFrame(response.get('data', []))
        return df

    def get_pcr(self, ticker: str, is_index: bool = True, on_field: str = 'OI', expiry: datetime = None) -> float:
        """
            Calculate the put-call ratio (PCR) for a given ticker.

            :param self: Represent the instance of the class
            :param ticker: The ticker symbol.
            :param is_index: Boolean value Specifies the given ticker is an index or not
            :param expiry: The expiry date of the option contract. Defaults to None.
            :param on_field: The field to calculate PCR on. `Volume` or `oi` (open-interest) Default to 'OI'.

            :return: The calculated PCR value
        """

        on_field = on_field.lower()
        if on_field not in self.valid_pcr_fields:
            print(f'Un-supported filed is passed only these are the fields available : {self.valid_pcr_fields}')
            return 0

        if expiry is None:
            df = self.get_option_chain(ticker, is_index=is_index)
        else:
            df = self.get_option_chain(ticker, is_index=is_index, expiry=expiry)

        if df.shape[0] == 0:
            print('Your filters lead to empty DataSet check all params, expiry, etc; returning 0 as default')
            return 0
        if on_field == 'oi':
            put_oi = df['PE_openInterest'].sum()
            call_oi = df['CE_openInterest'].sum()
            return put_oi / call_oi
        else:
            put_vol = df['PE_totalTradedVolume'].sum()
            call_vol = df['CE_totalTradedVolume'].sum()
            return put_vol / call_vol