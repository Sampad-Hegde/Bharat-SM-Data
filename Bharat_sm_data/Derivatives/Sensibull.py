from datetime import datetime

import pandas as pd
import pydash as _
import json

from Base import CustomSession


class Sensibull(CustomSession):
    """
        A class to interact with Sensibull API.

       Attributes:
           headers : dictionary containing the headers for the API requests

       Methods:
           __init__ : Initializes the Sensibull class instance
           _get_n_strikes_from_atm : Returns a list of strikes that are evenly spaced around the atm_strike by the
           strike gap
           search_token : Returns the token of a given symbol
           get_token_details : Returns the details of a given token
           get_options_data_with_greeks : Returns a dataframe with options data and greeks
    """

    def __init__(self):
        """
           The __init__ function is called when the class is instantiated.
           It sets up the instance of the class, and makes sure that it has all of its attributes.


           :param self: Represent the instance of the class

           :return: The instance of the class
        """

        super().__init__(headers={
            'authority': 'oxide.sensibull.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.8',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/110.0.0.0 Safari/537.36'
        })
        self._base_url = 'https://oxide.sensibull.com/v1/compute'
        try:
            self.session.get('https://sensibull.com/', headers=self.headers, timeout=10)
            self.session.get('https://web.sensibull.com/optionchain', headers=self.headers, timeout=10)
        except Exception as err:
            print(f"Error Occurred while setting cookies for SENSIBULL, Error MSG: {err}")

    # ----------------------------------------------------------------------------------------------------------------
    # Utility Functions

    @staticmethod
    def _get_n_strikes_from_atm(atm_strike: int, num_lookups: int, strike_gap: int) -> list:
        """
            The get_n_strikes_from_atm function takes in an atm_strike, num, and strike_gap.
            It returns a list of strikes that are evenly spaced around the atm_strike by the strike gap.
            The number of strikes returned is 2*num + 1.

            :param atm_strike: Determine the strike price of the `option`
            :param num_lookups: Determine the number of strikes to be generated to
            :param strike_gap: Determine the distance between each strike

            :return: A list of strikes
        """

        strikes = [atm_strike]
        down = atm_strike
        up = atm_strike
        for _ in range(num_lookups):
            down = down - strike_gap
            up = up + strike_gap
            strikes.append(int(down))
            strikes.append(int(up))
        return sorted(strikes)

    # ----------------------------------------------------------------------------------------------------------------
    # Generic Functions

    def search_token(self, symbol: str) -> dict:
        """
            The search_token function takes in a symbol and returns the token of that symbol.
                It does this by making a GET request to the Sensibull API, which returns an array of dictionaries.
                The function then searches through each dictionary for one with 'tradingsymbol' as key and
                'symbol' as value, returning its corresponding token.

            :param self: Represent the instance of the class
            :param symbol: Search for the underlying instrument in the response

            :return: The token of the symbol entered
        """

        response = self.hit_and_get_data(f'{self._base_url}/cache/underlying_instruments')
        response = response['data']
        result = _.find(response, {'tradingsymbol': symbol})
        return result

    def get_token_details(self, token: int) -> dict:
        """
            The get_token_details function takes in a token and returns the details of that token. The function first
            makes a GET request to the URL https://oxide.sensibull.com/v2/compute/cache/underlying_instruments,
            which returns an array of dictionaries containing information about all tokens on Sensibull's platform.

            :param self: Bind the method to an object
            :param token: Get the details of a particular token

            :return: The details of the token
        """

        response = self.hit_and_get_data(f'{self._base_url}/cache/underlying_instruments')
        response = response['data']
        result = _.find(response, {'instrument_token': token})
        return result

    # ----------------------------------------------------------------------------------------------------------------
    # Options (Greeks) Functions

    def get_options_data_with_greeks(self, ticker_data: dict, num_look_ups_from_atm: int, expiry_date: datetime) -> tuple:
        """
            The get_options_data_with_greeks function takes in the following parameters:
                ticker_data - a dictionary containing the instrument token and trading symbol of an underlying stock.
                num_look_ups_from_atm - number of strikes to look up from at-the-money strike price.
                expiry date - expiry date for which options data is required.

            :param self: Bind the method to an object
            :param ticker_data: Get the instrument_token of the underlying
            :param num_look_ups_from_atm: Get the number of strikes from atm strike
            :param expiry_date: Gets the data for that particular expiry date

            :return: A dataframe with the following columns:
        """

        response = self.hit_and_get_data(
            f'{self._base_url}/cache/live_derivative_prices/{ticker_data["instrument_token"]}')
        next_expiry = expiry_date.strftime('%Y-%m-%d')
        required_expiry_data = _.get(response, f"data.per_expiry_data.{next_expiry}", {})

        json_data = {'underlyer_list': [ticker_data["tradingsymbol"]]}
        resp = self.session.post('https://api.sensibull.com/v1/instrument_metadata/', headers=self.headers,
                                 json=json_data).json()
        mappings_data = json.loads(_.get(resp,
                                         f'derivatives.{ticker_data["tradingsymbol"]}'))
        mappings_data = _.get(mappings_data, f'derivatives.{next_expiry}.options')

        atm_strike = _.get(required_expiry_data, 'atm_strike')
        sorted_mappings_data_keys = sorted(list(mappings_data.keys()))
        atm_index = sorted_mappings_data_keys.index(str(atm_strike))
        strike_gap = int(float(sorted_mappings_data_keys[atm_index])) - int(
            float(sorted_mappings_data_keys[atm_index - 1]))
        strikes = self._get_n_strikes_from_atm(atm_strike, num_look_ups_from_atm, strike_gap)
        merged_data = []
        future_price = _.get(required_expiry_data, 'future_price', 0)
        required_expiry_data = required_expiry_data['options']

        for strike in strikes:
            call_maps = mappings_data[f'{float(strike)}']['CE']
            put_maps = mappings_data[f'{float(strike)}']['PE']
            call_data = _.find(required_expiry_data, {'token': call_maps['instrument_token']})
            put_data = _.find(required_expiry_data, {'token': put_maps['instrument_token']})
            merged_data.append({'future_price': future_price, 'CE': call_data, 'PE': put_data, 'strike': int(strike),
                                'CE.tradingsymbol': call_maps['tradingsymbol'],
                                'PE.tradingsymbol': put_maps['tradingsymbol']})
        df = pd.DataFrame(pd.json_normalize(merged_data))
        rm_cols = [x for x in df.columns.tolist() if 'token' in x or 'liquid' in x]
        df.drop(columns=rm_cols, inplace=True)
        return df, atm_strike

