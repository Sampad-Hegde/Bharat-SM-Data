from datetime import datetime

import pandas as pd
import pydash as _
from .CustomRequest import CustomSession


class NSEBase(CustomSession):
    """
        A class to interact with the NSE (National Stock Exchange) API.

        Attributes:
            _base_url: base URL for the NSE API

        Methods:
            __init__(): Initializes the class and sets up the session and headers for all subsequent requests.
            get_market_status_and_current_val(index: str = 'NIFTY 50') -> tuple: Returns the market status and current value of a given index.
            get_last_traded_date() -> datetime.date: Returns the last traded date of NIFTY 50 index.
            get_second_wise_data(ticker_or_index: str = "NIFTY 50", is_index: bool = True, underlying_symbol: str = None) -> pd.DataFrame: Returns a dataframe with second wise data for a given index or stock.
            get_ohlc_data(ticker_or_idx: str = "NIFTY 50", timeframe: str = '5Min', is_index: bool = True, underlying_symbol: str = None) -> pd.DataFrame: Returns the OHLC data for a given ticker or index.
            search(search_text: str) -> dict: Searches for data related to an equity, derivative, or any type of asset traded on NSE.
    """

    def __init__(self):
        """
            The __init__ function is called when the class is instantiated.
            It sets up the session and headers for all subsequent requests.
    
            :param self: Represent the instance of the class

            :return: Nothing
        """

        super().__init__(headers={
            'authority': 'www.nseindia.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.nseindia.com/',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54',
        })
        
        self._base_url = 'https://www.nseindia.com'
        self.hit_and_get_data(self._base_url)  
        # This will call the main website and sets cookies into a session object if available

    # ----------------------------------------------------------------------------------------------------------------
    # Utility Functions

    def get_market_status_and_current_val(self, index: str = 'NIFTY 50') -> tuple:
        """
            The get_market_status_and_current_val function returns the market status and current value of a given index.

            :param self: Represent the instance of the class
            :param index: Get the market status and last price of a particular index

            :return: A tuple of the market status and the current value
        """

        response = self.hit_and_get_data(f'{self._base_url}/api/marketStatus').get('marketState')
        status = _.get(_.find(response, {'index': 'NIFTY 50'}), 'marketStatus', 'Close')
        last_price = _.get(_.find(response, {'index': index}), 'last')
        return status, last_price

    def get_last_traded_date(self):
        """
            The get_last_traded_date function returns the last traded date of NIFTY 50 index.

            :param self: Represent the instance of the class
            :return: The date of the last traded day
        """
        response = self.hit_and_get_data(f'{self._base_url}/api/marketStatus').get('marketState')
        last_traded = _.get(_.find(response, {'index': 'NIFTY 50'}), 'tradeDate')
        return datetime.strptime(last_traded, '%d-%b-%Y %H:%M').date()

    # ----------------------------------------------------------------------------------------------------------------
    # Common Functions - works for both Equity as well index-related data fetches

    def get_second_wise_data(self, ticker_or_index: str = "NIFTY 50", is_index: bool = True, underlying_symbol: str = None) -> pd.DataFrame:
        """
            The get_second_wise_data function returns a dataframe with the following columns:
                timestamp - The time at which the price was recorded.
                price - The value of the index/stock at that particular time.

            :param self: Bind the method to a class
            :param ticker_or_index: Specify the index for which we want to get data
            :param is_index: (optional) Determine whether the index is an index or not
            :param underlying_symbol: (optional) This is required for fetching derivatives OHLC data where underlying
            assets ticker

            :return: A dataframe with second wise data
        """
        if not ticker_or_index.endswith('EQN') and not is_index:
            ticker_or_index += 'EQN'

        params = {'index': ticker_or_index}
        if is_index:
            params['indices'] = True

        if underlying_symbol is not None:
            params['underlyingsymbol'] = underlying_symbol
        response = self.hit_and_get_data(f'{self._base_url}/api/chart-databyindex', params=params)
        params['preopen'] = True
        pre_response = self.hit_and_get_data(f'{self._base_url}/api/chart-databyindex', params=params)

        df = pd.DataFrame(_.get(pre_response, 'grapthData', []) + _.get(response, 'grapthData', []),
                          columns=['timestamp', 'price'])
        df['timestamp'] = df['timestamp'] / 1000
        df['timestamp'] = df['timestamp'].apply(datetime.fromtimestamp)
        df['timestamp'] = df['timestamp'] - pd.Timedelta(hours=5, minutes=30)
        return df

    def get_ohlc_data(self, ticker_or_idx: str = "NIFTY 50", timeframe: str = '5Min', is_index: bool = True,
                      underlying_symbol: str = None) -> pd.DataFrame:
        """
            The get_ohlc_data function takes in a ticker or index name, and returns the OHLC data for that ticker/index.
            The function also takes in a timeframe parameter which can be used to specify the time interval of each
            candle. By default, it is set to 5 minutes.

            :param underlying_symbol: Index Symbol for options strikes
            :param self: Represents the instance of the class
            :param ticker_or_idx: Specify the ticker or index for which we want to get data
            :param timeframe: (optional) Define the time interval for which we want to get the data
            :param is_index: (optional) Determine whether the ticker is an index or a stock

            :return: The ohlc data for a given ticker or index
        """

        df = self.get_second_wise_data(ticker_or_idx, is_index, underlying_symbol)
        df.set_index(['timestamp'], inplace=True)
        df = df['price'].resample(timeframe).ohlc()
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Search and exchange related data

    def search(self, search_text: str) -> dict:
        """
            The search function can be used to take out data related to an Equity/ Derivatives or any type of asset
            traded on NSE, this is required to take out symbol/ticker ids respective to that asset

            :param self: Represent the instance of the class
            :param search_text: Specify the ticker or index for which we want to get data

            :return: The ohlc data for a given ticker or index
        """

        params = {
            'q': search_text,
        }

        response = self.hit_and_get_data(f'{self._base_url}/api/search/autocomplete', params=params)
        return response

    def get_nse_turnover(self) -> pd.DataFrame:
        """
            The `get_nse_turnover` provides the entire turnover happened in NSE exchange for the day / previous trading
            session as DataFrame.

           :param self: Represent the instance of the class

           :return: The exchange turnover data in the DataFrame format
       """

        response = self.hit_and_get_data(f'{self._base_url}/api/market-turnover-popup')
        df = pd.DataFrame(pd.json_normalize(response['data'], sep='_'))
        return df

    def get_nse_equity_meta_info(self, ticker: str) -> dict:
        params = {
            'symbol': ticker,
        }
        response = self.hit_and_get_data(f'{self._base_url}/api/equity-meta-info', params=params)
        return response
