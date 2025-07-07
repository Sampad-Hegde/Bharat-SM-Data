import pandas as pd

from Base import NSEBase

# constants

class NSE(NSEBase):
    """
        A class to interact with the NSE (National Stock Exchange) API.

        Attributes:
            mc : an instance of the MoneyControl class

        Methods:
            get_important_reports(report_name)
                Retrieves the data for a specific report from the NSE API.

                Args:
                    report_name: The name of the report.

                Returns:
                    The response of the request made to the NSE API.

            Get_equities_data_from_index(index='SECURITIES IN F&O')
                Retrieves a pandas dataframe containing information about equities from a specific index.

                Args:
                    index: The index for which to retrieve the data. Defaults to 'SECURITIES IN F&O'.

                Returns:
                    A dataframe with columns for symbol, series, security name, and last price.

            Get_all_indices()
                Retrieves a dataframe containing information about all indices.

                Returns:
                    A dataframe with information about all indices.

            Get_trade_info(ticker)
                Retrieves trade information for a given ticker or list of tickers.

                Args:
                    ticker: The ticker or list of tickers for which to retrieve trade information.

                Returns:
                    A dataframe with trade information.

            Get_corporate_disclosures(ticker)
                Retrieves corporate disclosures
    """

    def __init__(self) -> None:
        """
            It's a special function in Python classes, and it makes sure that every time you create a new instance of
            this class,
            the __init__ function gets called automatically to set up the attributes with their initial values.

            :param self: Represent the instance of the class

            :return: None
        """
        super().__init__()
        self._base_url = 'https://www.nseindia.com'
        self.hit_and_get_data(self._base_url)


    def get_important_reports(self) -> dict:
        """
            The get_important_reports function takes in a report_name and returns the data for that report.
            The function uses the try_n_times_get_response function to get a response from NSE's API.
            If there is no error, it will return the data for that particular report.

            :param self: Represents the instance of the class

            :return: A dict of objects which will give links to various reports
        """

        params = {'key': 'favCapital'}
        response = self.hit_and_get_data(f'{self._base_url}/api/merged-daily-reports', params=params)
        return response

    def get_equities_data_from_index(self, index='SECURITIES IN F&O'):
        """
            The get_equities_data_from_index function returns a dataframe containing the following information:
                - Symbol
                - Series (e.g. EQ, BE)
                - Security Name (e.g. ACC LIMITED)
                - Last Price (in Rs.)  # This is the last traded price of the equity on NSE for that day's trading session
                                       # at 15:30 IST or 16:00 IST depending on whether it is a normal trading day or
                                       not respectively

            :param self: Represent the instance of the class
            :param index: Specify the index for which we want to get the data

            :return: A dataframe with the following columns:
        """
        # Set the cookies
        self.hit_and_get_data(f'{self._base_url}/market-data/live-market-indices', params={'symbol': index})

        params = {
            'index': index.upper(),
        }
        response = self.hit_and_get_data(f'{self._base_url}/api/equity-stockIndices', params=params)
        df = pd.DataFrame(pd.json_normalize(response['data'], sep='_'))
        rm_cols = [x for x in df.columns.to_list() if x.startswith('chart') or x.startswith('meta_is')
                   or x.startswith('meta_tempSuspended') or x.startswith('meta_debtSeries')
                   or x.startswith('meta_activeSeries')]
        df.drop(columns=rm_cols, inplace=True)
        return df

    def get_all_indices(self):
        """
            This will give a complete dataframe of all indices and its minimalistic data like OHLC

            :param self: Represents the instance of the class

            :return: A DataFrame of all indices traded on NSE
        """
        # Set the cookies
        self.hit_and_get_data(f'{self._base_url}/market-data/live-market-indices')

        response = self.hit_and_get_data("https://www.nseindia.com/api/allIndices")
        df = pd.DataFrame(response.get('data', {}))
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Equity/ETF/SGB Related Data
    def get_trade_info(self, ticker: list or str) -> pd.DataFrame:
        """
            Get trade information for one or more ticker(s).

            :param self: Represents the instance of the class
            :param ticker: this can a string represents single ticker ot list tickers.

            :return: DataFrame containing the trade information for the given ticker(s).
        """

        if type(ticker) == str:
            tickers = [ticker]
        else:
            tickers = ticker
        data = []
        for ticker in tickers:
            params = {
                'symbol': ticker,
            }
            # set the cookies
            self.hit_and_get_data(f'{self._base_url}/get-quotes/equity', params=params)

            complete_equity_info = {}
            for section in ['', 'trade_info']:
                params['section'] = section
                if section == '':
                    del params['section']
                response = self.hit_and_get_data(f'{self._base_url}/api/quote-equity', params=params)
                complete_equity_info.update(response)
            data.append(complete_equity_info)
        df = pd.DataFrame(pd.json_normalize(data, sep='_'))
        return df

    def get_corporate_disclosures(self, ticker: list or str) -> dict:
        """
            Get corporate disclosure data

            :param self: Represents the instance of the class
            :param ticker: this can a string represents single ticker ot list tickers.

            :return: DataFrame contains the corporate disclosures data
        """

        if type(ticker) == str:
            tickers = [ticker]
        else:
            tickers = ticker
        data = {}
        for ticker in tickers:
            # set the cookies
            self.hit_and_get_data(f'{self._base_url}/get-quotes/equity', params={'symbol': ticker})

            params = {
                'symbol': ticker,
                'market': 'equities'
            }
            response = self.hit_and_get_data(f'{self._base_url}/api/top-corp-info', params=params)
            data[ticker] = response
        return data

    def get_sme_stocks(self):
        """
            Get SME (Small Medium Enterprises) data

            :param self: Represents the instance of the class

            :return: DataFrame containing SME Stocks data.
        """
        # set the cookies
        self.hit_and_get_data(f'{self._base_url}/market-data/sme-market')

        response = self.hit_and_get_data(f'{self._base_url}/api/live-analysis-emerge')
        df = pd.DataFrame(response.get('data', []))
        return df

    def get_sgb_data(self):
        """
            Get trade information of Sovereign Gold Bonds data

            :param self: Represents the instance of the class

            :return: DataFrame containing the trade information for SGB.
        """
        # set the cookies
        self.hit_and_get_data(f'{self._base_url}/market-data/sovereign-gold-bond')

        response = self.hit_and_get_data(f'{self._base_url}/api/sovereign-gold-bonds')
        df = pd.DataFrame(response.get('data', []))
        df.drop(columns=['meta'], inplace=True)
        return df

    def get_all_etf(self):
        """
            Get trade information of all ETFs (Exchange Traded Funds)

            :param self: Represents the instance of the class

            :return: DataFrame containing data of all ETFs
        """
        # set the cookies
        self.hit_and_get_data(f'{self._base_url}/market-data/exchange-traded-funds-etf')

        response = self.hit_and_get_data(f'{self._base_url}/api/etf')
        df = pd.DataFrame(response.get('data', []))
        df.drop(columns=['meta'], inplace=True)
        return df

    def get_all_today_block_deals(self):
        """
            Get trade information for all block deals happened today;

            :param self: Represents the instance of the class

            :return: DataFrame containing block deals data.
        """
        # set the cookies
        self.hit_and_get_data(f'{self._base_url}/market-data/block-deal-watch')

        response = self.hit_and_get_data(f'{self._base_url}/api/block-deal')
        df = pd.DataFrame(response.get('data', []))
        return df

    def get_india_vix(self, interval: str) -> pd.DataFrame:
        """
            This will fetch the OHLCV datapoints of the INDIA Volatility Index.

            :param interval: Time interval for the data ('1d' for daily qnd '1' for 1min)

            :return: DataFrame containing the India VIX data for last 2months or ~1780 OHLCV datapoints
        """
        print("INDIA VIX is No Longer Available on NSE India :( ")
        print("Please Use INDIA VIX from MONEYCONTROL")
        print("""
        from Fundamentals import MoneyControl
        moneycontrol = MoneyControl()
        moneycontrol.get_india_vix(interval='1') # Only `1d` (for day interval) or `1`  (for minute interval) is supported
        """)    
        # return self.get_ohlc_data('INDIA VIX', timeframe=interval)
        return pd.DataFrame()