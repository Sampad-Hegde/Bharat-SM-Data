import json

import pandas as pd
import pydash as _
from bs4 import BeautifulSoup

from Base import CustomSession


class Tickertape(CustomSession):
    """
        A class to interact with the Tickertape API.

        Attributes:
            valid_horizons : list of valid time horizons for financial data
            valid_search_places: list of valid search places for ticker search

        Methods:
            __init__ : Initialize the Tickertape class
            get_ticker : Get the ticker symbol and raw response for a given hint and search place
            _get_url_of_the_ticker : Get the URL of the ticker
            get_all_nifty_50_ticker : Get a list of tickers for the Nifty 50 index
            get_all_constituents_of_index : Get a list of tickers for a given index
            get_income_data : Get income data for a given ticker and time horizon
            get_balance_sheet_data : Get balance sheet data for a given ticker
            get_cash_flow_data : Get cash flow data for a given ticker
            peers_comparison : Get peer comparison data for a given ticker and comparison type
            get_score_card : Get the scorecard for a given ticker
            get_share_holding_pattern : Get the share holding pattern for a given ticker
            get_mutual_fund_holdings : Get the mutual fund holdings for a given ticker
    """

    def __init__(self, custom_headers: dict=None, custom_cookies: dict=None) -> None:
        """
            The __init__ function is called when the class is instantiated.
            It's a special function in Python classes, and it makes sure that every time you create a new instance of
            this class,
            the __init__ function gets called automatically to set up the attributes with their initial values.

            :param self: Represent the instance of the class
            :param custom_headers: (optional) Allow the user to pass custom headers to the session
            :param custom_cookies: (optional) Allow the user to pass custom cookies to the session

            :return: The session and headers
        """
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': '',
            'accept-version': '7.9.0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36'
        }
        if custom_headers:
            self.headers.update(custom_headers)

        super().__init__(headers=self.headers)
        if custom_cookies:
            self.session.cookies.update(self.cookies)
        self._base_url = 'https://api.tickertape.in'
        self.valid_horizons = ['interim', 'annual']
        self.valid_search_places = ['stock', 'index', 'etf', 'mutualfund', 'space', 'profile', 'smallcase']

    # ----------------------------------------------------------------------------------------------------------------
    # Basic Utility Functions
    def get_ticker(self, hint, search_place='all') -> tuple:
        """
            The get_ticker function takes a hint and search_place as arguments.
            The hint is the name of the company you are looking for, and search_place can be one of:
                - all (default)
                - stocks
                - funds # mutual funds, ETFs etc.

            :param self: Represent the instance of the class
            :param hint: Search for the ticker
            :param search_place: Specify the type of search you want to perform
            :return: A tuple with the first hit and all hits
        """
        if search_place == 'all':
            search_place = ','.join(self.valid_search_places)
        elif search_place not in self.valid_search_places:
            raise Exception(f'You are providing wrong type of search; valid searches are : {self.valid_search_places} '
                            f'and you can pass `all` in other case')

        params = {
            'text': hint,
            'types': search_place,
            'pageNumber': 0

        }

        response = self.hit_and_get_data(f"{self._base_url}/search", params=params)
        raw = _.get(response, 'data.items', {})
        first_hit = raw[0].get('sid', '')
        return first_hit, raw

    def _get_url_of_the_ticker(self, ticker: str) -> str:
        """
            Get the URL of a ticker

            :param self: Bind the method to an object
            :param ticker: Search for the stock or index you want to get data on

            :return: Tuple contains the ticker and the raw response
        """

        _, raw = self.get_ticker(ticker)
        for datapoints in raw:
            if datapoints.get('ticker') == ticker:
                return datapoints.get('slug')
        return '/'

    def get_all_nifty_50_ticker(self) -> list:
        """
            The get_nifty_50_ticker function returns a list of tickers for the Nifty-50 index.
            The function uses the hit_and_get_data function to get a response from
            https://api.tickertape.in/indices/constituents/.NSEI, which is an API that provides data on
            constituents of various indices in India, including the Nifty 50 index.

            :param self: Represents the instance of the class

            :return: A list of tickers
        """

        tickertape_tickers = []
        response = self.hit_and_get_data(f'{self._base_url}/indices/constituents/.NSEI')
        for tick in response['data']['constituents']:
            tickertape_tickers.append(tick['sid'])
        return tickertape_tickers

    def get_all_constituents_of_index(self, index: str) -> pd.DataFrame:
        """
            This will give all equities that are part of an index.

            :param self: Represents the instance of the class
            :param index: The index name; for example .NSEI (nifty 50), .NIFTY500 (nifty 500)

            :return: A list of tickers
        """

        response = self.hit_and_get_data(f'{self._base_url}/indices/constituents/{index}')
        df = pd.DataFrame(response.get('data', {}).get('constituents', []))
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Annual Report/ Quarterly Results extracted data

    def get_income_data(self, ticker: str, time_horizon: str = 'interim', num_time_periods: int = 10,
                        view_type: str = 'normal') -> pd.DataFrame:
        """
            Get income data for a given ticker.

            :param self: Represents the instance of the class
            :param ticker: The ticker symbol of the stock
            :param time_horizon: The time horizon of the income data (interim / annual). Defaults to 'interim'
            :param num_time_periods: The number of time periods to retrieve. Default to 10.
            :param view_type: The view type of the income data (normal / growth). Defaults to 'normal'.

            :return: The DataFrame containing income data
        """

        if time_horizon not in self.valid_horizons:
            print(f'Error You have passed wrong time horizon, valid horizons are : {self.valid_horizons}')
            return pd.DataFrame()

        if view_type not in ['normal', 'growth', 'margin']:
            print(f"Error You have passed wrong view type, valid view types are : {['normal', 'growth', 'margin']}")
            return pd.DataFrame()

        params = {'count' : num_time_periods}
        response = self.hit_and_get_data(
            f'{self._base_url}/stocks/financials/income/{ticker}/{time_horizon}/{view_type}', params=params)
        df = pd.DataFrame(response.get('data', []))
        return df

    def get_balance_sheet_data(self, ticker: str, num_time_periods: int = 10, growth: bool = False) -> pd.DataFrame:
        """
            Get balance sheet data for a given ticker.

            :param self: Represents the instance of the class
            :param ticker: The ticker symbol of the stock
            :param num_time_periods: The number of time periods to retrieve. Default to 10.
            :param growth: Boolean flag tell the report is normal type or growth type.

            :return: The DataFrame containing balance sheet data
        """

        if growth:
            growth_type = 'growth'
        else:
            growth_type = 'normal'

        params = {'count': num_time_periods}
        response = self.hit_and_get_data(
            f'{self._base_url}/stocks/financials/balancesheet/{ticker}/annual/{growth_type}', params=params)
        df = pd.DataFrame(response.get('data', []))
        return df

    def get_cash_flow_data(self, ticker: str, num_time_periods: int = 10, growth: bool = False) -> pd.DataFrame:
        """
            Get cash flow data for a given ticker.

            :param self: Represents the instance of the class
            :param ticker: The ticker symbol of the stock
            :param num_time_periods: The number of time periods to retrieve. Default to 10.
            :param growth: Boolean flag tell the report is normal type or growth type.

            :return: The DataFrame containing cash flow data
        """

        if growth:
            growth_type = 'growth'
        else:
            growth_type = 'normal'

        params = {'count': num_time_periods}
        response = self.hit_and_get_data(
            f'{self._base_url}/stocks/financials/cashflow/{ticker}/annual/{growth_type}', params=params)
        df = pd.DataFrame(response.get('data', []))
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Peer Comparisons

    def peers_comparison(self, ticker: str, comparison_type: str = 'valuation') -> pd.DataFrame:
        """
            Fetches and returns comparison data for a given ticker.

            :param self: Represents the instance of the class
            :param ticker: The ticker symbol of the stock
            :param comparison_type: Type of comparison (valuation/technical). Defaults to 'valuation'.

            :return: The DataFrame containing the peers comparison result
        """

        comparison_type = comparison_type.lower()
        params = {
            'tab': comparison_type
        }
        response = self.hit_and_get_data(f'{self._base_url}/stocks/peers/{ticker}', params=params)
        df = pd.DataFrame(pd.json_normalize(response.get('data', []), sep='_'))
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # TickerTape Score cards

    def get_score_card(self, ticker) -> pd.DataFrame:
        """
            Get the scorecard for a given ticker.

            :param self: Represents the instance of the class
            :param ticker: The ticker symbol of the stock

            :return: The DataFrame contains all key flags like valuation, technical, growth red flags, etc.
        """

        response = self.hit_and_get_data(f'https://analyze.api.tickertape.in/stocks/scorecard/{ticker}')
        df = pd.DataFrame(pd.json_normalize(response.get('data', []), sep='_'))
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Share Holding Patterns

    def get_share_holding_pattern(self, stock_slug_endpoint: str) -> pd.DataFrame:
        """
            Get the share holding pattern for a given ticker.

            :param self: Represents the instance of the class
            :param stock_slug_endpoint: It's the part of url expect base url which navigates to the
                                        stock profile in the website. You can get this from search url raw data.
                                        For example, if stock url is `https://www.tickertape.in/stocks/hdfc-bank-HDBK`
                                        then `stocks/hdfc-bank-HDBK` is the slug url.

            :return: The DataFrame contains the share holding pattern.
        """

        response = self.session.get(f'https://www.tickertape.in/{stock_slug_endpoint}')
        soup = BeautifulSoup(response.text, features="html5lib")
        sp_div = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        data = json.loads(sp_div.contents[0].text)
        data = data.get('props').get('pageProps').get('securitySummary').get('holdings').get('holdings')
        df = pd.DataFrame(pd.json_normalize(data, sep='_'))
        return df

    def get_mutual_fund_holdings(self, stock_slug_endpoint: str) -> pd.DataFrame:
        """
            Get mutual fund holdings for a given ticker.

            :param self: Represents the instance of the class
            :param stock_slug_endpoint: It's the part of url expect base url which navigates to the
                                        stock profile in the website. You can get this from search url raw data.
                                        For example, if stock url is `https://www.tickertape.in/stocks/hdfc-bank-HDBK`
                                        then `stocks/hdfc-bank-HDBK` is the slug url.

            :return: The DataFrame contains the mutual fund holdings.
        """

        response = self.session.get(f'https://www.tickertape.in/{stock_slug_endpoint}')
        soup = BeautifulSoup(response.text, features="html5lib")
        sp_div = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        data = json.loads(sp_div.contents[0].text)
        data = data.get('props').get('pageProps').get('securitySummary').get('mfHoldings')
        df = pd.DataFrame(pd.json_normalize(data, sep='_'))
        return df

    def get_smallcase_holdings(self, stock_slug_endpoint: str) -> pd.DataFrame:
        """
            Get smallcase holdings for a given ticker.

            :param self: Represents the instance of the class
            :param stock_slug_endpoint: It's the part of url expect base url which navigates to the
                                        stock profile in the website. You can get this from search url raw data.
                                        For example, if stock url is `https://www.tickertape.in/stocks/hdfc-bank-HDBK`
                                        then `stocks/hdfc-bank-HDBK` is the slug url.

            :return: The DataFrame containing smallcase holdings for the given ticker
        """

        response = self.session.get(f'https://www.tickertape.in/{stock_slug_endpoint}')
        soup = BeautifulSoup(response.text, features="html5lib")
        sp_div = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        data = json.loads(sp_div.contents[0].text)
        data = data.get('props').get('pageProps').get('securitySummary').get('smallcases')
        df = pd.DataFrame(data)
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Dividends and important ratios
    def get_dividends_history(self, stock_slug_endpoint: str) -> pd.DataFrame:
        """
            Gets the dividend history for a given stock ticker.

            :param self: Represents the instance of the class
            :param stock_slug_endpoint: It's the part of url expect base url which navigates to the
                                        stock profile in the website. You can get this from search url raw data.
                                        For example, if stock url is `https://www.tickertape.in/stocks/hdfc-bank-HDBK`
                                        then `stocks/hdfc-bank-HDBK` is the slug url.

            :return: The DataFrame contains the dividend history
        """

        response = self.session.get(f'https://www.tickertape.in/{stock_slug_endpoint}')
        soup = BeautifulSoup(response.text, features="html5lib")
        sp_div = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        data = json.loads(sp_div.contents[0].text)
        data = data.get('props').get('pageProps').get('securitySummary').get('dividends')
        df = pd.DataFrame(data.get('past', []) + data.get('upcoming', []))
        return df

    def get_key_ratios(self, stock_slug_endpoint: str) -> pd.DataFrame:
        """
            Get key ratios for a given stock ticker.

            :param self: Represents the instance of the class
            :param stock_slug_endpoint: It's the part of url expect base url which navigates to the
                                        stock profile in the website. You can get this from search url raw data.
                                        For example, if stock url is `https://www.tickertape.in/stocks/hdfc-bank-HDBK`
                                        then `stocks/hdfc-bank-HDBK` is the slug url.

            :return: A transposed DataFrame containing the key ratios for the stock.
        """

        response = self.session.get(f'https://www.tickertape.in/{stock_slug_endpoint}')
        soup = BeautifulSoup(response.text, features="html5lib")
        sp_div = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        data = json.loads(sp_div.contents[0].text)
        data = data.get('props').get('pageProps').get('securityInfo').get('ratios')
        df = pd.DataFrame([data])
        return df.T

    # ----------------------------------------------------------------------------------------------------------------
    # ETF related data

    def get_all_etfs_under_index(self, index: str) -> pd.DataFrame:
        """
            Get all ETFs under a specific index.

            :param self: Represents the instance of the class
            :param index: A valid index traded on Indian Exchange.

            :return: A DataFrame containing the ETF data.
        """

        response = self.hit_and_get_data(f'{self._base_url}/indices/etfs/{index}')
        df = pd.DataFrame(pd.json_normalize(response.get('data', []), sep='_'))
        return df

    # ----------------------------------------------------------------------------------------------------------------_
    # Equity Research Filters

    def get_equity_screener_all_filters(self) -> dict:
        """
            The get_equity_screener_all_filters function returns a dictionary of all the filters available for equity screener.
            The key is the display name and value is label name.

            :param self: Represent the instance of the class.
            :return: A dictionary of all the filters that can be used in the equity screener.
        """
        response = self.hit_and_get_data(f'{self._base_url}/screener/filters')
        all_filters = {}
        for filters_type in response.get('data'):
            for fltr in response.get('data').get(filters_type):
                if not fltr.get('premium'):
                    all_filters[fltr.get('display')] = fltr.get('label')

        return all_filters

    def get_equity_screener_data(self, filters: list, sortby: str = None,
                                 number_of_records: int = None) -> pd.DataFrame:
        """
            !! Carefully call this function because this is a heavy and time-consuming function.
            Save the data once you get the data to save resource and time !!

            The get_equity_screener_data function is used to retrieve equity screener data from the
                https://api.kite.trade/screener/query endpoint of the Kite Connect API.

            :param self: Represent the instance of the class
            :param filters: list: Define the columns that you want to be returned in your dataframe you can pass all
            filters which are non-premium aka values list of `get_equity_screener_all_filters` function returned
            dictionary.
            :param sortby: str: Sort the dataframe by a specific column if you don't pass this it will consider the 1st
            value of filters list.
            :param number_of_records: int: Limit the number of records that are returned
            :return: A pandas dataframe with the all data you asked in the `filters` field. You can save this data
            df and use it for your research
        """
        if sortby is None and sortby in filters:
            sortby = filters[0]
        elif sortby is not None and sortby not in filters:
            print("You can't sort on filed which is even not in your filters projection")

        if number_of_records is None:
            number_of_records = float('inf')

        main_df = pd.DataFrame()
        page = 1
        while True:
            json_data = {
                'match': {},
                'sortBy': sortby,
                'sortOrder': -1,
                'project': filters,
                'offset': (page - 1) * 20,
                'count': 20,
                'sids': [],
            }

            response = self.session.post(f'{self._base_url}/screener/query', headers=self.headers,
                                         json=json_data).json()
            df = pd.DataFrame(response.get('data').get('results'))
            if df.shape[1] == 0 or page * 20 > number_of_records:
                break
            main_df = pd.concat([main_df, df], ignore_index=True)
            page += 1
        main_df['stock'].apply(lambda x: x.get('advancedRatios'))
        data = pd.json_normalize(main_df['stock'])
        data['sid'] = main_df['sid']
        return data

