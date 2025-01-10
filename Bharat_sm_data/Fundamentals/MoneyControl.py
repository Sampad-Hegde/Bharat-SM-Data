import io
import warnings
import json
import math
from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from pydash.collections import find

from Base import CustomSession

warnings.filterwarnings('ignore')

class MoneyControl(CustomSession):
    """
        A class to control money-related operations.

       Attributes:
           No Attributes

       Methods:
        __init__(): Initializes the MoneyControl class.
        get_ticker(search_text: str) -> tuple: Retrieve the ticker for a given search text.
       _get_all_extracted_urls(main_url: str): Retrieve all extracted URLs from the main URL.
       _common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages): Extracts
       data from the given URL and returns a DataFrame.
       get_india_vix(interval: str) -> pd.DataFrame: Retrieves India Vix data for a given interval.
       get_overview_mini_statement(ticker: str, statement_type: str = 'consolidated',
       statement_frequency: int = 12): Retrieve the overview mini statement for a given ticker.
       get_income_mini_statement(ticker: str, statement_type: str = 'consolidated', statement_frequency: int = 12):
       Retrieves the income mini statement for a given ticker.
       get_balance_sheet_mini_statement(ticker: str,
       statement_type: str = 'consolidated'): Retrieves the balance sheet mini statement for a given ticker.

    """

    def __init__(self) -> None:
        """
            The __init__ function gets called automatically to set up the attributes with their initial values.

            :param self: Represent the instance of the class
        """

        super().__init__(headers={
            'Accept': 'application/json, text/plain, */*',
            'Referer': '',
            'accept-version': '7.9.0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0'
        })
        self._base_url = 'https://www.moneycontrol.com'
        self.hit_and_get_data(f'{self._base_url}/')
        self.valid_intervals_for_vix = ['1',  # 1 min
                                        '1d',  # 1 day
                                        ]
        self.valid_reports_type = {'consolidated': 'C', 'standalone': 'S'}

    # ----------------------------------------------------------------------------------------------------------------
    # Basic Utility Functions
    def get_ticker(self, search_text: str) -> tuple:
        """
            Get ticker information for a given search text.

           :param self: Represent the instance of the class.
           :param search_text: The text to search for.

           :return: A tuple containing the stock ID and the corresponding object (raw data).
       """

        params = {
            'classic': 'true',
            'query': search_text,
            'type': '1',
            'format': 'json',
            'callback': 'suggest1',
        }

        response = self.session.get(f'{self._base_url}/mccode/common/autosuggestion_solr.php/',
                                    params=params)
        resp = json.loads(response.text[9:-1])
        obj = find(resp, {'stock_name': search_text})

        if obj is not None:
            return obj['sc_id'], obj

        return resp[0]['sc_id'], resp

    def _get_all_extracted_urls(self, main_url: str) -> dict:
        """
            Get all extracted URLs from a main URL.

           :param self: Represent the instance of the class.
           :param main_url: The main URL to extract URLs from.

           :return: A list of strikes
       """

        response = self.session.get(main_url, headers=self.headers)
        soup = BeautifulSoup(response.text, features="html5lib")
        ul = soup.find('div', class_='quick_links clearfix').find('ul')
        urls = {}
        for li in ul.find_all('li'):
            url = li.a['href']
            text = li.a.get_text()
            urls[text] = url
        return urls

    def _common_complete_sheet_data_extractor(self, company_mc_url: str, statement_type: str, report_data: dict, pages: int) -> pd.DataFrame:
        """
            It's a helper function that reduces some re-occurring functions;
            Extracts complete sheet data for a given company, statement type, report data, and number of pages.

            :param self: Represent the instance of the class.
            :param company_mc_url: Moneycontrol URL for the company
            :param statement_type: Type of the statement (consolidated or standalone)
            :param report_data: key value pair which gives report name and its key-name
            :param pages: Number of pages to extract data from (1 page = 5 time-periods)

            :return: Extracted data as a DataFrame
       """

        data_url = self._get_all_extracted_urls(company_mc_url).get(report_data.get('report_name')).split('#')[0]
        main_df = pd.DataFrame()
        if statement_type == 'consolidated':
            data_url = data_url.replace(report_data.get('report_code'),
                                        f"consolidated-{report_data.get('report_code')}")
        for page in range(pages):
            try:
                response = self.session.get(f'{data_url}/{page + 1}', headers=self.headers)
            except:
                print(f'Only till {page + 1} is available; so, returning data collected so far')
                return main_df
            df = pd.read_html(io.StringIO(response.text))[0]
            df.columns = df.iloc[0]
            merge_col = df.iloc[0][0]
            df = df[1:]
            df.drop(columns=[df.columns.to_list()[-1]], inplace=True)
            if page == 0:
                main_df = df
            else:
                main_df = main_df.merge(df, on=merge_col, how='left')
        return main_df

    # ----------------------------------------------------------------------------------------------------------------
    # India Vix
    def get_india_vix(self, interval: str) -> pd.DataFrame:
        """
           This will fetch the OHLCV datapoints of the INDIA Volatility Index.

           :param self: Represent the instance of the class.
           :param interval: Time interval for the data ('1d' for daily qnd '1' for 1min)

           :return: DataFrame containing the India VIX data for last 2months or ~1780 OHLCV datapoints
       """

        end = datetime.now()  # set to now for getting latest vix
        start = end - timedelta(days=60)
        params = {
            'symbol': 'in;IDXN',
            'resolution': interval,
            'from': int(start.timestamp()),
            'to': int(end.timestamp()),
            'countback': '1782',
            'currencyCode': 'INR',
        }
        response = self.hit_and_get_data('https://priceapi.moneycontrol.com/techCharts/history', params=params)
        try:
            del response['s']
        except Exception as err:
            print(f'Deleting Exception!! Error : {err}')

        df = pd.DataFrame.from_dict(response)
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Mini Statements regd financials of Equity
    def get_overview_mini_statement(self, ticker: str, statement_type: str = 'consolidated',
                                    statement_frequency: int = 12) -> pd.DataFrame:
        """
           This will give highly extracted and most commonly used data from quarterly/annual reports
           this is good for quick comparisons, as it suggests it will give mini statements
           which means it will give data only for few time periods (quarterly/annual/6months/9months)

           :param self: Represent the instance of the class.
           :param ticker: The moneycontrol ticker symbol of the company.
           :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
           Defaults to 'consolidated'.
           :param statement_frequency: (Optional) The frequency of the statement. Defaults to 12.

           :return: The processed data in a DataFrame format.
       """

        valid_frequencies = [3, 12]
        statement_type = statement_type.lower()
        try:
            statement_type = self.valid_reports_type[statement_type]
        except:
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        if statement_frequency not in valid_frequencies:
            print(f'Invalid statement frequency passed; these are the only allowed statements : {valid_frequencies}')
            return pd.DataFrame()
        params = {
            'classic': 'true',
            'referenceId': 'overview',
            'requestType': statement_type,
            'scId': ticker,
            'frequency': str(statement_frequency)
        }
        response = self.session.get(f'{self._base_url}/mc/widget/mcfinancials/getFinancialData',
                                    params=params)
        soup = BeautifulSoup(response.text, features="html5lib")
        try:
            data = json.loads(soup.find('div', attrs={'id': f'{statement_type}-{statement_frequency}-graph'}).contents[0].text)
        except Exception as err:
            print(f'Exception happened while parsing webpage pls check all params once again; Error Message : {err}')

        processed_data = {
            'headings': []
        }
        for i in data:
            processed_data['headings'].append(i['heading'])
            for j in i['data']:
                if j['year'] not in processed_data.keys():
                    processed_data[j['year']] = [j['value']]
                else:
                    processed_data[j['year']].append(j['value'])
        df = pd.DataFrame(processed_data)
        return df

    def get_income_mini_statement(self, ticker: str, statement_type: str = 'consolidated',
                                  statement_frequency: int = 12) -> pd.DataFrame:
        """
           This will give highly extracted and most commonly used data from quarterly/annual reports
           this is good for quick comparisons, as it suggests it will give mini statements
           which means it will give data only for few time periods (quarterly/annual/6months/9months)

           :param self: Represent the instance of the class.
           :param ticker: The moneycontrol ticker symbol of the company.
           :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
           Defaults to 'consolidated'.
           :param statement_frequency: (Optional) The frequency of the statement. Defaults to 12.

           :return: The company income data in a DataFrame format.
       """

        valid_frequencies = [3, 6, 9, 12]
        statement_type = statement_type.lower()
        try:
            statement_type = self.valid_reports_type[statement_type]
        except:
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        if statement_frequency not in valid_frequencies:
            print(f'Invalid statement frequency passed; these are the only allowed statements : {valid_frequencies}')
            return pd.DataFrame()
        params = {
            'classic': 'true',
            'referenceId': 'income',
            'requestType': statement_type,
            'scId': ticker,
            'frequency': str(statement_frequency)
        }
        response = self.session.get(f'{self._base_url}/mc/widget/mcfinancials/getFinancialData',
                                    params=params)
        df = pd.read_html(io.StringIO(response.text))[0]
        df.drop(columns=[df.columns.to_list()[-1]], inplace=True)  # drop the trend column
        return df

    def get_balance_sheet_mini_statement(self, ticker: str, statement_type: str = 'consolidated') -> pd.DataFrame:
        """
           This will give highly extracted and most commonly used data from quarterly/annual reports
           this is good for quick comparisons, as it suggests it will give mini statements
           which means it will give data only for few time periods (quarterly/annual/6months/9months)

           :param self: Represent the instance of the class.
           :param ticker: The moneycontrol ticker symbol of the company.
           :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
           Defaults to 'consolidated'.

           :return: The company balance sheet data in a DataFrame format.
        """

        statement_type = statement_type.lower()
        try:
            statement_type = self.valid_reports_type[statement_type]
        except:
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        params = {
            'classic': 'true',
            'referenceId': 'balance-sheet',
            'requestType': statement_type,
            'scId': ticker
        }
        response = self.session.get(f'{self._base_url}/mc/widget/mcfinancials/getFinancialData',
                                    params=params)
        dfs = pd.read_html(io.StringIO(response.text))
        annual_headers = dfs[0].columns.to_list()
        annual_headers[0] = 'headers'
        for df in dfs:
            df.columns = annual_headers
        df = pd.concat(dfs, ignore_index=True)
        df.drop(columns=[df.columns.to_list()[-1]], inplace=True)  # drop the trend column
        return df

    def get_cash_flow_mini_statement(self, ticker: str, statement_type: str = 'consolidated') -> pd.DataFrame:
        """
           This will give highly extracted and most commonly used data from quarterly/annual reports
           this is good for quick comparisons, as it suggests it will give mini statements
           which means it will give data only for few time periods (quarterly/annual/6months/9months)

           :param self: Represent the instance of the class.
           :param ticker: The moneycontrol ticker symbol of the company.
           :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
           Defaults to 'consolidated'.

           :return: The company's cash flow statements data in a DataFrame format.
       """

        statement_type = statement_type.lower()
        try:
            statement_type = self.valid_reports_type[statement_type]
        except:
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        params = {
            'classic': 'true',
            'referenceId': 'cash-flow',
            'requestType': statement_type,
            'scId': ticker,
        }
        response = self.session.get(f'{self._base_url}/mc/widget/mcfinancials/getFinancialData',
                                    params=params)
        df = pd.read_html(io.StringIO(response.text))[0]
        df.drop(columns=[df.columns.to_list()[-1]], inplace=True)  # drop the trend column
        return df

    def get_ratios_mini_statement(self, ticker: str, statement_type: str = 'consolidated') -> pd.DataFrame:
        """
           This will give highly extracted and most commonly used data from quarterly/annual reports
           this is good for quick comparisons, as it suggests it will give mini statements
           which means it will give data only for few time periods (quarterly/annual/6months/9months)

           :param self: Represent the instance of the class.
           :param ticker: The moneycontrol ticker symbol of the company.
           :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
           Defaults to 'consolidated'.

           :return: The company's key performance ratios in DataFrame format.
        """

        statement_type = statement_type.lower()
        try:
            statement_type = self.valid_reports_type[statement_type]
        except:
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        params = {
            'classic': 'true',
            'referenceId': 'ratios',
            'requestType': statement_type,
            'scId': ticker
        }
        response = self.session.get(f'{self._base_url}/mc/widget/mcfinancials/getFinancialData',
                                    params=params)
        dfs = pd.read_html(io.StringIO(response.text))
        annual_headers = dfs[0].columns.to_list()
        annual_headers[0] = 'ratios'
        for df in dfs:
            df.columns = annual_headers
        df = pd.concat(dfs, ignore_index=True)
        df.drop(columns=[df.columns.to_list()[-1]], inplace=True)  # drop the trend column
        return df

    # ----------------------------------------------------------------------------------------------------------------
    # Complete Statements regd financials of Equity

    def get_complete_balance_sheet(self, company_mc_url: str, statement_type: str = 'standalone', num_years: int = 5) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)
            :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
            Defaults to 'standalone'.
            :param num_years: (Optional) Number of years for which balance sheet data is required (min 5,
            and it should be multiple of 5)

            :return: Complete balance sheet data in the DataFrame format.
        """

        pages = math.ceil(num_years / 5)
        if statement_type not in self.valid_reports_type.keys():
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        report_data = {'report_name': 'Balance Sheet', 'report_code': 'balance-sheet'}
        return self._common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages)

    def get_complete_profit_loss(self, company_mc_url: str, statement_type: str = 'standalone', num_years: int = 5) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)
            :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
            Defaults to 'standalone'.
            :param num_years: (Optional) Number of years for which a P&L statement is required (min 5,
            and it should be multiple of 5)

            :return: Complete P&L statement data in the DataFrame format.
        """

        pages = math.ceil(num_years / 5)
        if statement_type not in self.valid_reports_type.keys():
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        report_data = {'report_name': 'Profit & Loss', 'report_code': 'profit-loss'}
        return self._common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages)

    def get_complete_quarterly_results(self, company_mc_url: str, statement_type: str = 'standalone',
                                       num_quarters: int = 5) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)
            :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
            Defaults to 'standalone'.
            :param num_quarters: (Optional) Number of quarters for which quarterly results are required (min 5,
            and it should be multiple of 5)

            :return: Complete quarterly (25th percentile of the year) results data in the DataFrame format.
        """

        pages = math.ceil(num_quarters / 5)
        if statement_type not in self.valid_reports_type.keys():
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        report_data = {'report_name': 'Quarterly Results', 'report_code': 'quarterly-result'}
        return self._common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages)

    def get_complete_half_yearly_results(self, company_mc_url: str, statement_type: str = 'standalone',
                                         num_half_years: int = 5) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)
            :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
            Defaults to 'standalone'.
            :param num_half_years: (Optional) Number of 6months data is required (min 5,
            and it should be multiple of 5)

            :return: Complete half-yearly (50th percentile of the year) results data in the DataFrame format.
        """

        pages = math.ceil(num_half_years / 5)
        if statement_type not in self.valid_reports_type.keys():
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        report_data = {'report_name': 'Half Yearly Results', 'report_code': 'half-yearly'}
        return self._common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages)

    def get_complete_nine_months_results(self, company_mc_url: str, statement_type: str = 'standalone',
                                         num_nine_months: int = 5) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)
            :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
            Defaults to 'standalone'.
            :param num_nine_months: (Optional) Number of 9months data is required (min 5,
            and it should be multiple of 5)

            :return: Complete nine-months (75th percentile of the year) data in the DataFrame format.
        """

        pages = math.ceil(num_nine_months / 5)
        if statement_type not in self.valid_reports_type.keys():
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        report_data = {'report_name': 'Nine Months Results', 'report_code': 'nine-months'}
        return self._common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages)

    def get_complete_yearly_results(self, company_mc_url: str, statement_type: str = 'standalone',
                                    num_years: int = 5) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)
            :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
            Defaults to 'standalone'.
            :param num_years: (Optional) The Number of annual reports is required (min 5,
            and it should be multiple of 5)

            :return: Complete annual (100th percentile of the year) report data in the DataFrame format.
        """

        pages = math.ceil(num_years / 5)
        if statement_type not in self.valid_reports_type.keys():
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        report_data = {'report_name': 'Yearly Results', 'report_code': 'yearly'}
        return self._common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages)

    def get_complete_cashflow_statement(self, company_mc_url: str, statement_type: str = 'standalone',
                                        num_years: int = 5) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)
            :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
            Defaults to 'standalone'.
            :param num_years: (Optional) The Number of annual reports is required (min 5,
            and it should be multiple of 5)

            :return: Complete cash-flow statements data in the DataFrame format.
        """

        pages = math.ceil(num_years / 5)
        if statement_type not in self.valid_reports_type.keys():
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        report_data = {'report_name': 'Cash Flows', 'report_code': 'cash-flow'}
        return self._common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages)

    def get_complete_ratios_data(self, company_mc_url: str, statement_type: str = 'standalone',
                                 num_years: int = 5) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)
            :param statement_type: (Optional) The type of statement to retrieve (consolidated / standalone).
            Defaults to 'standalone'.
            :param num_years: (Optional) The number of annual reports is required (min 5,
            and it should be multiple of 5)

            :return: Complete key ratios data in the DataFrame format.
        """

        pages = math.ceil(num_years / 5)
        if statement_type not in self.valid_reports_type.keys():
            print(
                f'Invalid statement type passed; these are the only allowed statements : {self.valid_reports_type.keys()}')
            return pd.DataFrame()
        report_data = {'report_name': 'Ratios', 'report_code': 'ratios'}
        return self._common_complete_sheet_data_extractor(company_mc_url, statement_type, report_data, pages)

    def get_complete_capital_structure_statement(self, company_mc_url: str) -> pd.DataFrame:
        """
            This will give complete data of quarterly/annual reports.
            This is a complete report that can be used any fundamental deep analysis

            :param self: Represent the instance of the class.
            :param company_mc_url: Company's main MoneyControl url (this can be taken from get_ticker() function)

            :return: Complete capital Structure data in the DataFrame format.
        """

        data_url = self._get_all_extracted_urls(company_mc_url).get('Capital Structure')
        response = self.session.get(f'{data_url}', headers=self.headers)
        df = pd.read_html(io.StringIO(response.text))[0]
        return df
    