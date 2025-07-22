
import pandas as pd
from time import sleep
from io import StringIO
from bs4 import BeautifulSoup

from Base import CustomSession 



class Screener(CustomSession):
    """
    The Screener class is used to interact with the Screener.in website to fetch financial data for companies.
    It allows users to log in, search for companies, and retrieve various financial tables such as quarterly results,
    profit and loss statements, balance sheets, cash flow statements, ratios, and shareholding patterns.
    It also provides methods to fetch company textual data and perform ticker searches.

    Attributes:
        username (str): The username for logging into Screener.in.
        password (str): The password for logging into Screener.in.
    
    Methods:
        __init__(username: str, password: str) -> None:
            Initializes the Screener class with a session and CSRF token for login.
        get_ticker(symbol_name: str) -> list:
            Fetches the ticker symbol for a given company name from Screener.
        get_company_textual_data(ticker: str) -> str:
            Fetches the textual data of a company from Screener.
        get_base_tables(ticker_url: str, table: str) -> pd.DataFrame:
            Fetches the key points table for a given ticker URL.
        get_quarterly_results(ticker_url: str) -> pd.DataFrame:
            Fetches the quarterly results table for a given ticker URL.
        get_profit_and_loss(ticker_url: str) -> pd.DataFrame:
            Fetches the Profit & Loss table for a given ticker URL.
        get_balance_sheet(ticker_url: str) -> pd.DataFrame:
            Fetches the Balance Sheet table for a given ticker URL.
        get_cash_flow(ticker_url: str) -> pd.DataFrame:
            Fetches the Cash Flow table for a given ticker URL.
        get_ratios(ticker_url: str) -> pd.DataFrame:
            Fetches the Ratios table for a given ticker URL.
        get_shareholding_pattern(ticker_url: str) -> pd.DataFrame:
            Fetches the Shareholding Pattern table for a given ticker URL.
        get_peers_comparison(ticker_url: str) -> pd.DataFrame:
            Fetches the peers comparison table for a given ticker URL.
        get_chart_data(ticker_url: str, timeframe: str = '1d', start_date: str = None, end_date: str = None) -> pd.DataFrame:
            Fetches the chart data for a given ticker URL and timeframe.
        get_screeners() -> list:
            Fetches the list of available screeners from Screener.in.
        get_query_from_pre_screens_feed(ticker_url: str) -> str:
            Fetches the query from the pre-screens feed for a given ticker URL.
        get_all_industries() -> list:
            Fetches the list of all industries available on Screener.in.
        get_industry_wise_data(industry_url: str) -> pd.DataFrame:
            Fetches the industry-wise Stocks for a given industry URL.
        get_concall_list(ticker_url: str) -> pd.DataFrame:
            Fetches the concall list for a given ticker URL.
    """
    def __init__(self, username: str, password: str) -> None:
        """
        Initializes the Screener class with a session and CSRF token for login.
        
        :param username: The username for login.
        :param password: The password for login.
        """
        self._username = username
        self._password = password
        self._csrf_token = None
        self._login_csrf_token = None
        self.base_url = 'https://www.screener.in'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://www.screener.in',
            'Priority': 'u=0, i'
        }
        all_supported_columns = ['Sales', 'OPM', 'Profit after tax', 'Market Capitalization', 'Sales latest quarter', 'Profit after tax latest quarter', 'YOY Quarterly sales growth', 'YOY Quarterly profit growth', 'Price to Earning', 'Dividend yield', 'Price to book value', 'Return on capital employed', 'Return on assets', 'Debt to equity', 'Return on equity', 'EPS', 'Debt', 'Promoter holding', 'Change in promoter holding', 'Earnings yield', 'Pledged percentage', 'Industry PE', 'Sales growth', 'Profit growth', 'Current price', 'Price to Sales', 'Price to Free Cash Flow', 'EVEBITDA', 'Enterprise Value', 'Current ratio', 'Interest Coverage Ratio', 'PEG Ratio', 'Return over 3months', 'Return over 6months', 'Is SME', 'Is not SME', 'Number of equity shares', 'Equity capital', 'Preference capital', 'Reserves', 'Secured loan', 'Unsecured loan', 'Balance sheet total', 'Gross block', 'Revaluation reserve', 'Accumulated depreciation', 'Net block', 'Capital work in progress', 'Investments', 'Current assets', 'Current liabilities', 'Book value of unquoted investments', 'Market value of quoted investments', 'Contingent liabilities', 'Cash from operations last year', 'Free cash flow last year', 'Cash from investing last year', 'Cash from financing last year', 'Net cash flow last year', 'Cash beginning of last year', 'Cash end of last year', 'Sales last year', 'Operating profit last year', 'Other income last year', 'EBIDT last year', 'Depreciation last year', 'EBIT last year', 'Interest last year', 'Profit before tax last year', 'Tax last year', 'Profit after tax last year', 'Extraordinary items last year', 'Net Profit last year', 'Dividend last year', 'Material cost last year', 'Employee cost last year', 'OPM last year', 'NPM last year', 'Operating profit latest quarter', 'Other income latest quarter', 'EBIDT latest quarter', 'Depreciation latest quarter', 'EBIT latest quarter', 'Interest latest quarter', 'Profit before tax latest quarter', 'Tax latest quarter', 'Extraordinary items latest quarter', 'Net Profit latest quarter', 'GPM latest quarter', 'OPM latest quarter', 'NPM latest quarter', 'Equity Capital latest quarter', 'EPS latest quarter', 'Price to Quarterly Earning', 'Book value', 'Inventory turnover ratio', 'Quick ratio', 'Exports percentage', 'Total Assets', 'Piotroski score', 'G Factor', 'Operating profit', 'Interest', 'Depreciation', 'EPS last year', 'EBIT', 'Net profit', 'Asset Turnover Ratio', 'Financial leverage', 'Current Tax', 'Tax', 'Operating profit 2quarters back', 'Operating profit 3quarters back', 'Sales 2quarters back', 'Sales 3quarters back', 'Net profit 2quarters back', 'Net profit 3quarters back', 'Working capital', 'Number of Shareholders', 'Unpledged promoter holding', 'Return on invested capital', 'Lease liabilities', 'Inventory', 'Trade receivables', 'Debtor days', 'Industry PBV', 'Operating profit growth', 'Other income', 'Volume 1month average', 'Volume 1week average', 'Volume', 'High price', 'Low price', 'High price all time', 'Low price all time', 'Face value', 'Credit rating', 'Working Capital to Sales ratio', 'QoQ Profits', 'QoQ Sales', 'Net worth', 'Market Cap to Sales', 'Interest Coverage', 'Enterprise Value to EBIT', 'Debt Capacity', 'Debt To Profit', 'Total Capital Employed', 'CROIC', 'debtplus', 'Leverage', 'Dividend Payout', 'Intrinsic Value', 'cash debt contingent liabilities by mcap', 'Cash by market cap', '52w Index', 'Down from 52w high', 'Up from 52w low', 'From 52w high', 'Mkt Cap To Debt Cap', 'Dividend Payout Ratio', 'Graham', 'Price to Cash Flow', 'ROCE3yr avg', 'Working Capital Days', 'Cash Equivalents', 'Earning Power', 'PB X PE', 'Graham Number', 'NCAVPS', 'Market Capt to Cash Flow', 'Altman Z Score', 'Cash Conversion Cycle', 'Advance from Customers', 'Trade Payables', 'Days Payable Outstanding', 'Days Receivable Outstanding', 'Days Inventory Outstanding', 'Market cap to quarterly profit', 'Return over 1day', 'Return over 1week', 'Return over 1month', 'Last result date', 'Last annual result date', 'Expected quarterly sales growth', 'Expected quarterly sales', 'Expected quarterly operating profit', 'Expected quarterly net profit', 'Expected quarterly EPS', 'DMA 50', 'DMA 200', 'DMA 50 previous day', 'DMA 200 previous day', 'RSI', 'MACD', 'MACD Previous Day', 'MACD Signal', 'MACD Signal Previous Day', 'Public holding', 'FII holding', 'Change in FII holding', 'DII holding', 'Change in DII holding', 'Number of equity shares preceding year', 'Free cash flow preceding year', 'Cash from operations preceding year', 'Cash from investing preceding year', 'Cash from financing preceding year', 'Net cash flow preceding year', 'Cash beginning of preceding year', 'Cash end of preceding year', 'Sales preceding year', 'Operating profit preceding year', 'Other income preceding year', 'EBIDT preceding year', 'Depreciation preceding year', 'EBIT preceding year', 'Interest preceding year', 'Profit before tax preceding year', 'Tax preceding year', 'Profit after tax preceding year', 'Extraordinary items preceding year', 'Net Profit preceding year', 'Dividend preceding year', 'OPM preceding year', 'NPM preceding year', 'Sales preceding quarter', 'Operating profit preceding quarter', 'Other income preceding quarter', 'EBIDT preceding quarter', 'Depreciation preceding quarter', 'EBIT preceding quarter', 'Interest preceding quarter', 'Profit before tax preceding quarter', 'Tax preceding quarter', 'Profit after tax preceding quarter', 'Extraordinary items preceding quarter', 'Net Profit preceding quarter', 'OPM preceding quarter', 'NPM preceding quarter', 'Equity Capital preceding quarter', 'EPS preceding quarter', 'Book value preceding year', 'Return on capital employed preceding year', 'Return on assets preceding year', 'EPS preceding year', 'Return on equity preceding year', 'Debt preceding year', 'Sales preceding 12months', 'Net profit preceding 12months', 'Working capital preceding year', 'Number of Shareholders preceding quarter', 'Net block preceding year', 'Gross block preceding year', 'Capital work in progress preceding year', 'Sales growth 3Years', 'Sales growth 5Years', 'Profit growth 3Years', 'Profit growth 5Years', 'Average return on equity 5Years', 'Average return on equity 3Years', 'Return over 1year', 'Return over 3years', 'Return over 5years', 'Number of equity shares 10years back', 'Free cash flow 3years', 'Free cash flow 5years', 'Free cash flow 7years', 'Free cash flow 10years', 'Sales preceding year quarter', 'Operating profit preceding year quarter', 'Other income preceding year quarter', 'EBIDT preceding year quarter', 'Depreciation preceding year quarter', 'EBIT preceding year quarter', 'Interest preceding year quarter', 'Profit before tax preceding year quarter', 'Tax preceding year quarter', 'Profit after tax preceding year quarter', 'Extraordinary items preceding year quarter', 'Net Profit preceding year quarter', 'OPM preceding year quarter', 'NPM preceding year quarter', 'Equity Capital preceding year quarter', 'EPS preceding year quarter', 'Book value 3years back', 'Book value 5years back', 'Book value 10years back', 'Inventory turnover ratio 3Years back', 'Inventory turnover ratio 5Years back', 'Inventory turnover ratio 7Years back', 'Inventory turnover ratio 10Years back', 'Sales growth 10years median', 'Sales growth 5years median', 'Sales growth 7Years', 'Sales growth 10Years', 'EBIDT growth 3Years', 'EBIDT growth 5Years', 'EBIDT growth 7Years', 'EBIDT growth 10Years', 'EPS growth 3Years', 'EPS growth 5Years', 'EPS growth 7Years', 'EPS growth 10Years', 'Profit growth 7Years', 'Profit growth 10Years', 'Exports percentage 3Years back', 'Exports percentage 5Years back', 'Average 5years dividend', 'Average return on capital employed 3Years', 'Average return on capital employed 5Years', 'Average return on capital employed 7Years', 'Average return on capital employed 10Years', 'Average return on equity 10Years', 'Average return on equity 7Years', 'Return on equity 5years growth', 'Operating cash flow 3years', 'Operating cash flow 5years', 'Operating cash flow 7years', 'Operating cash flow 10years', 'Investing cash flow 10years', 'Investing cash flow 7years', 'Investing cash flow 5years', 'Investing cash flow 3years', 'OPM 5Year', 'OPM 10Year', 'Working capital 3Years back', 'Working capital 5Years back', 'Working capital 7Years back', 'Working capital 10Years back', 'Debt 3Years back', 'Debt 5Years back', 'Debt 7Years back', 'Debt 10Years back', 'Number of Shareholders 1year back', 'Change in promoter holding 3Years', 'Average dividend payout 3years', 'Net block 3Years back', 'Net block 5Years back', 'Net block 7Years back', 'Cash 3Years back', 'Cash 5Years back', 'Cash 7Years back', 'Average debtor days 3years', 'Debtor days 3years back', 'Debtor days 5years back', 'Return on assets 5years', 'Return on assets 3years', 'Historical PE 3Years', 'Historical PE 10Years', 'Historical PE 7Years', 'Historical PE 5Years', 'Volume 1year average', 'Average Earnings 5Year', 'Average Earnings 10Year', 'Average EBIT 5Year', 'Average EBIT 10Year', 'Market Capitalization 3years back', 'Market Capitalization 5years back', 'Market Capitalization 7years back', 'Market Capitalization 10years back', 'Average Working Capital Days 3years', 'Return over 7years', 'Return over 10years', 'Change in FII holding 3Years', 'Change in DII holding 3Years']
        super().__init__(headers=headers)
        if username and password:
            login_session = self.session.get(url=f'{self.base_url}/login/', headers=self.headers)
            soup = BeautifulSoup(login_session.text, 'html.parser')
            self._csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
            print("CSRF Token fetched successfully", self._csrf_token)

            payload = {
                'username': self._username,
                'password': self._password,
                'csrfmiddlewaretoken': self._csrf_token
            }
            login = self.session.post(f'{self.base_url}/login/', data=payload, headers=self.headers)
            if login.status_code == 200:
                login_soup = BeautifulSoup(login.text, 'html.parser')
                self._login_csrf_token = login_soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
                error_message = login_soup.find('ul', class_='errorlist nonfield')
                if error_message:
                    print("Error during login:", error_message.text.strip())
                elif not self._login_csrf_token:
                    print("Login failed: CSRF token is missing after login.")
                else:
                    print("Login successful! ", self._login_csrf_token)
                    

            else:
                print("Login failed with status code:", login.status_code)
    
    def get_ticker(self, symbol_name: str) -> list:
        """
        Fetches the ticker symbol for a given company name from Screener.

        :param symbol_name: The name of the company to fetch the ticker for (some prefix string to search).

        :return: The ticker symbol of the company.
        """
        params = {
            'q': symbol_name,
            'v' : 3,
            'fts': 1
        }
        search_res = self.hit_and_get_data(
            url=f'{self.base_url}/api/company/search/',
            params=params
        )
        return search_res
    
    def get_company_textual_data(self, ticker: str) -> str:
        """
        Fetches the textual data of a company from Screener.

        :param company_name: The name of the company to fetch data for.

        :return: The textual data of the company.
        """
        if not self._login_csrf_token:
            raise Exception("Login failed. CSRF token is missing.")
        
        url = f'{self.base_url}/wiki/company/{ticker}/commentary/edit'
        response = self.session.get(url, headers=self.headers)
        
        if response.status_code == 200 and self._login_csrf_token is not None:
            soup = BeautifulSoup(response.text, 'html.parser')
            try:
                text_data = soup.find('input', {'name': 'old_content'})['value']
                return text_data
            except Exception as e:
                print('Data is Un-parsable or not available for this ticker:', ticker)
        else:
            raise Exception(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")
        
    def get_base_tables(self, ticker_url: str, table: str) -> pd.DataFrame:
        """
        Fetches the key points table for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.
        :param table: The type of table to fetch (e.g., 'Quarterly Results', 'Profit & Loss', etc.).

        :return: A DataFrame containing the key points table.
        """
        order = ['Quarterly Results', 'Profit & Loss', 'Compounded Sales Growth', 'Compounded Profit Growth', 'Stock Price CAGR',  'Return on Equity', 'Balance Sheet', 'Cash Flow', 'Ratios', 'Shareholding Pattern', 'ALL']
        if table not in order:
            raise ValueError(f"Table '{table}' is not a valid table type. Valid options are: {order}")
        
        response = self.session.get(self.base_url+ticker_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        company_id = soup.find('div', {'id': 'company-info'})['data-company-id']
        if response.status_code == 200 and self._login_csrf_token is not None:
            dfs = pd.read_html(StringIO(response.text))
            return dfs[order.index(table)] if table != 'ALL' else dfs, company_id
        
    def get_quarterly_results(self, ticker_url: str) -> pd.DataFrame:
        """
        Fetches the quarterly results table for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.

        :return: A DataFrame containing the quarterly results table.
        """
        base_df, company_id = self.get_base_tables(ticker_url, 'Quarterly Results')
        try:
            base_df = base_df.set_index('Unnamed: 0')
        except Exception as e:
            print("Error setting index for base DataFrame:", e)
        consolidated = True if 'consolidated' in ticker_url else False
        extra_urls = []
        for row_idx in base_df.index:
            if row_idx.endswith('+'):
                extra_urls.append({'parent': row_idx.rstrip('+'), 'section': 'quarters'})

        datapoints = dict()  
        if consolidated:
            for param in extra_urls:
                param['consolidated'] = True
                url = f'{self.base_url}/api/company/{company_id}/schedules/'
                extra_data = self.hit_and_get_data(
                    url=url,
                    params=param
                )
                datapoints.update(extra_data)
        else:
            for param in extra_urls:
                url = f'{self.base_url}/api/company/{company_id}/schedules/'
                extra_data = self.hit_and_get_data(
                    url=url,
                    params=param
                )
                datapoints.update(extra_data)
        
        extra_df = pd.DataFrame.from_dict(datapoints, orient='index')
        extra_df.index.name = 'Unnamed: 0'
        df = pd.concat([base_df, extra_df], axis=0)
        df.drop(columns=['setAttributes'], inplace=True, errors='ignore') if 'setAttributes' in df.columns else None
        return df
                
    def get_profit_and_loss(self, ticker_url: str) -> pd.DataFrame:
        """
        Fetches the Profit & Loss table for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.

        :return: A DataFrame containing the Profit & Loss table.
        """
        base_df, company_id = self.get_base_tables(ticker_url, 'Profit & Loss')
        try:
            base_df = base_df.set_index('Unnamed: 0')
        except Exception as e:
            print("Error setting index for base DataFrame:", e)
        consolidated = True if 'consolidated' in ticker_url else False

        extra_urls = []
        for row_idx in base_df.index:
            if row_idx.endswith('+'):
                extra_urls.append({'parent': row_idx.rstrip('+'), 'section': 'profit-loss'})

        datapoints = dict()
        if consolidated:
            for param in extra_urls:
                param['consolidated'] = True
                url = f'{self.base_url}/api/company/{company_id}/schedules/'
                extra_data = self.hit_and_get_data(
                    url=url,
                    params=param
                )
                datapoints.update(extra_data)
        else:
            for param in extra_urls:
                url = f'{self.base_url}/api/company/{company_id}/schedules/'
                extra_data = self.hit_and_get_data(
                    url=url,
                    params=param
                )
                datapoints.update(extra_data)
        extra_df = pd.DataFrame.from_dict(datapoints, orient='index')
        extra_df.index.name = 'Unnamed: 0'
        df = pd.concat([base_df, extra_df], axis=0)
        df.drop(columns=['setAttributes'], inplace=True, errors='ignore') if 'setAttributes' in df.columns else None
        return df
    
    def get_balance_sheet(self, ticker_url: str) -> pd.DataFrame:
        """
        Fetches the Balance Sheet table for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.

        :return: A DataFrame containing the Balance Sheet table.
        """
        base_df, company_id = self.get_base_tables(ticker_url, 'Balance Sheet')
        try:
            base_df = base_df.set_index('Unnamed: 0')
        except Exception as e:
            print("Error setting index for base DataFrame:", e)

        consolidated = True if 'consolidated' in ticker_url else False

        extra_urls = []
        for row_idx in base_df.index:
            if row_idx.endswith('+'):
                extra_urls.append({'parent': row_idx.rstrip('+'), 'section': 'balance-sheet'})
        
        datapoints = dict()
        if consolidated:
            for param in extra_urls:
                param['consolidated'] = True
                url = f'{self.base_url}/api/company/{company_id}/schedules/'
                extra_data = self.hit_and_get_data(
                    url=url,
                    params=param
                )
                datapoints.update(extra_data)
        else:
            for param in extra_urls:
                url = f'{self.base_url}/api/company/{company_id}/schedules/'
                extra_data = self.hit_and_get_data(
                    url=url,
                    params=param
                )
                datapoints.update(extra_data)
        extra_df = pd.DataFrame.from_dict(datapoints, orient='index')
        extra_df.index.name = 'Unnamed: 0'
        df = pd.concat([base_df, extra_df], axis=0)
        df.drop(columns=['setAttributes'], inplace=True, errors='ignore') if 'setAttributes' in df.columns else None
        return df
    
    def get_cash_flow(self, ticker_url: str) -> pd.DataFrame:
        """
        Fetches the Cash Flow table for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.

        :return: A DataFrame containing the Cash Flow table.
        """
        base_df, company_id = self.get_base_tables(ticker_url, 'Cash Flow')
        try:
            base_df = base_df.set_index('Unnamed: 0')
        except Exception as e:
            print("Error setting index for base DataFrame:", e)

        consolidated = True if 'consolidated' in ticker_url else False

        extra_urls = []
        for row_idx in base_df.index:
            if row_idx.endswith('+'):
                extra_urls.append({'parent': row_idx.rstrip('+'), 'section': 'cash-flow'})
        
        datapoints = dict()
        if consolidated:
            for param in extra_urls:
                param['consolidated'] = True
                url = f'{self.base_url}/api/company/{company_id}/schedules/'
                extra_data = self.hit_and_get_data(
                    url=url,
                    params=param
                )
                datapoints.update(extra_data)
        else:
            for param in extra_urls:
                url = f'{self.base_url}/api/company/{company_id}/schedules/'
                extra_data = self.hit_and_get_data(
                    url=url,
                    params=param
                )
                datapoints.update(extra_data)
        
        extra_df = pd.DataFrame.from_dict(datapoints, orient='index')
        extra_df.index.name = 'Unnamed: 0'
        df = pd.concat([base_df, extra_df], axis=0)
        df.drop(columns=['setAttributes'], inplace=True, errors='ignore') if 'setAttributes' in df.columns else None
        return df

    def get_ratios(self, ticker_url: str) -> pd.DataFrame:
        """
        Fetches the Ratios table for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.

        :return: A DataFrame containing the Ratios table.
        """
        base_df, company_id = self.get_base_tables(ticker_url, 'Ratios')
        try:
            base_df = base_df.set_index('Unnamed: 0')
        except Exception as e:
            print("Error setting index for base DataFrame:", e)
        return base_df        

    def get_shareholding_pattern(self, ticker_url: str) -> pd.DataFrame:
        """
        Fetches the Shareholding Pattern table for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.

        :return: A DataFrame containing the Shareholding Pattern table.
        """
        base_df, company_id = self.get_base_tables(ticker_url, 'Shareholding Pattern')
        try:
            base_df = base_df.set_index('Unnamed: 0')
        except Exception as e:
            print("Error setting index for base DataFrame:", e)
        
        entities = ['promoters', 'public', 'foreign_institutions', 'domestic_institutions', 'government']

        datapoints = dict()
        for entity in entities:
            url = f'{self.base_url}/api/3/{company_id}/investors/{entity}/quarterly/'
            extra_data = self.hit_and_get_data(url=url)
            datapoints.update(extra_data)
        extra_df = pd.DataFrame.from_dict(datapoints, orient='index')
        extra_df.index.name = 'Unnamed: 0'
        df = pd.concat([base_df, extra_df], axis=0)
        df.drop(columns=['setAttributes'], inplace=True, errors='ignore') if 'setAttributes' in df.columns else None
        return df

    def get_peers_comparison(self, ticker_url: str) -> pd.DataFrame:
        """
        Fetches the peers comparison table for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.

        :return: A DataFrame containing the peers comparison table.
        """
        response = self.session.get(self.base_url+ticker_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        company_id = soup.find('div', {'id': 'company-info'})['data-warehouse-id']

        peers_html = self.session.get(
            url=f'{self.base_url}/api/company/{company_id}/peers/',
            headers=self.headers
        )
        if peers_html.status_code == 200:
            dfs = pd.read_html(StringIO(peers_html.text))
            if dfs:
                peers_df = dfs[0]
                return peers_df
            else:
                raise ValueError("No data found in the peers comparison table.")
    
    def get_chart_data(self, ticker_url: str, days=365, on='Price-DMA50-DMA200-Volume') -> pd.DataFrame:
        """
        Fetches the chart data for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.
        :param days: The number of days for which to fetch the chart data (default is 365).
        :param on: The type of chart data to fetch (default is 'Price-DMA50-DMA200-Volume').

        :return: A DataFrame containing the chart data.
        """
        valid_on_options = ['Price-DMA50-DMA200-Volume', 'Price to Earning-Median PE-EPS', 'GPM-OPM-NPM-Quarter Sales', 'EV Multiple-Median EV Multiple-EBITDA', 'Price to book value-Median PBV-Book value', 'Market Cap to Sales-Median Market Cap to Sales-Sales']
        if on not in valid_on_options:
            raise ValueError(f"Invalid 'on' option. Valid options are: {valid_on_options}")

        _, company_id = self.get_base_tables(ticker_url, 'Stock Price CAGR')

        params = {'q': on, 'days': days}
        if 'consolidated' in ticker_url:
            params['consolidated'] = True

        chart_data = self.hit_and_get_data(
            url=f'{self.base_url}/api/company/{company_id}/chart/',
            params=params
        )

        chart_data = chart_data.get('datasets', [])
        processed_data = {}
        for item in chart_data:
            metric = item.get('label', 'NA')
            points = [x[1] for x in item.get('values', [])]
            if 'date' not in processed_data:
                processed_data['date'] = [x[0] for x in item.get('values', [])]
            processed_data[metric] = points
        try:
            return pd.DataFrame.from_dict(processed_data)
        except Exception as e:
            print("Error creating DataFrame from chart data:", e)
            return chart_data
       
    def get_screens(self) -> list:
        """
        Fetches the list of screens available on Screener tab Feeds.

        :return: A list of screens.
        """
        response = self.session.get(f'{self.base_url}/explore', headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        screens_tags = soup.find_all('a', class_='screen-item')
        screens = {}
        for tag in screens_tags:
            screen_name = tag.find('div').text.strip()
            screen_url = tag['href']
            screens[screen_name] = screen_url
        return screens
    
    def get_query_from_pre_screens_feed(self, screen_url: str) -> str:
        """
        Fetches the query from a pre-defined screen URL.

        :param screen_url: The URL of the pre-defined screen.

        :return: The query string used in the screen.
        """
        response = self.session.get(f'{self.base_url}{screen_url}', headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        query_tag = soup.find('textarea', {'name': 'query'})
        if query_tag:
            return query_tag.text.strip()
        else:
            raise ValueError("No query found for the given screen URL.")
    
    def get_data_from_screen_query(self, query: str, columns: list=[]) -> pd.DataFrame:
        """
        Fetches data from a screen query.

        :param query: The query string to fetch data for.

        :return: A DataFrame containing the data from the screen query.
        """
        if len(columns) > 0:
            response = self.session.post(
                f'{self.base_url}/user/columns/',
                json={'csrfmiddlewaretoken': self._login_csrf_token,'data': columns},
            )
            soup = BeautifulSoup(response.text, 'html.parser')
            error = soup.find('li', class_='manage-columns error')
            if error:
                raise ValueError(f"Error: setting columns requires Premium Account: {error.text.strip().replace('\n', ' ')}")
            else:
                print("Columns set successfully.")

        pg = 1
        df = pd.DataFrame()
        while pg:
            params = {'sort': '', 'order': '', 'query': query, 'page': pg, 'limit': 50}
            try:
                response = self.session.get(f'{self.base_url}/screen/raw', params=params, headers=self.headers)
                temp_df = pd.read_html(StringIO(response.text))
            except Exception as e:
                print(f"Error fetching data for page {pg}: {e}")
                temp_df = None
            if temp_df:
                temp_df = temp_df[0]
                if temp_df.empty:
                    break
                else:
                    df = pd.concat([temp_df, df], ignore_index=True)
            else:
                print("No data found for the given query.")
                break
            sleep(5)  # To avoid hitting the server too hard
            pg += 1
        try:
            df = df[df['S.No.'] != 'S.No.']
            df.drop(columns=['S.No.'], inplace=True, errors='ignore')
        except Exception as e:
            pass
        return df
    
    def get_all_industries(self) -> list:
        """
        Fetches all industries available on Screener.

        :return: A list of industries.
        """
        response = self.session.get(f'{self.base_url}/market/', headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        links_map = {}
        for tag in soup.find_all('a', {'class': 'font-weight-500'}):
            if tag.get('href'):
                links_map[tag.text.strip()] = tag.get('href')
        industries_df = pd.DataFrame.from_dict(links_map, orient='index', columns=['URL'])
        
        df = pd.read_html(StringIO(response.text))
        if df:
            df = df[0]
            df = df.set_index('Industry')
            df = df.join(industries_df)
            df.index.name = 'Industry'
            df.drop('S.No.', axis=1, inplace=True, errors='ignore')
            return df
        else:
            raise ValueError("No industries found on Screener.")
    
    def get_industry_wise_data(self, industry_url: str) -> pd.DataFrame:
        """
        Fetches data for a specific industry from Screener.

        :param industry_url: The URL of the industry page.

        :return: A DataFrame containing the industry data.
        """
        response = self.session.get(f'{self.base_url}{industry_url}', headers=self.headers)
        tables = pd.read_html(StringIO(response.text))
        if tables:
            df = tables[0]
        else:
            raise ValueError("No data found for the given industry URL.")
        soup = BeautifulSoup(response.text, 'html.parser')
        has_next = soup.find('div', {'class': 'pagination'})
        try:
            last_page = int((has_next.find_all('a', {'class': 'ink-900'})[-1]).text.strip()) if has_next else 0
        except Exception as e:
            last_page = 1
        page = 2
        print('Fetching Pages ... 1.', end="\t")
        while page <= last_page:
            try:
                response = self.session.get(f'{self.base_url}{industry_url}', headers=self.headers, params={'page': page})
                tables = pd.read_html(StringIO(response.text))
            except Exception as e:
                print(f"Error fetching data for page {page}: {e}")
                print(response.text)
                break

            if tables:
                temp_df = tables[0]
                if not temp_df.empty:
                    df = pd.concat([df, temp_df], ignore_index=True)
                else:
                    break
            else:
                break
            sleep(5)
            print(f"{page}.", end="\t")
            page += 1
        print("Done")
        try:
            df = df[df['S.No.'] != 'S.No.']
            df = df[df['Name'].str.startswith('Median:') == False]
            df.drop(columns=['S.No.'], inplace=True, errors='ignore')
        except Exception as e:
            pass
        return df.reset_index(drop=True)

    def get_cocalls_link(self, ticker_url: str) -> str:
        """
        Fetches the CoCalls link for a given ticker URL.

        :param ticker_url: The URL of the company's ticker page.

        :return: The CoCalls link for the company.
        """
        response = self.session.get(self.base_url+ticker_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        concalls = {}
        for tag in soup.findAll('li', {'class': 'flex flex-gap-8 flex-wrap'}):
            name = tag.find('div', {'class': 'ink-600 font-size-15 font-weight-500 nowrap'})
            transcript = tag.find('a', {'class': 'concall-link', 'title': 'Raw Transcript'})
            notes = tag.find('button', {'class': 'concall-link plausible-event-name=Concall+Notes plausible-event-user=free'})
            ppt = tag.find('a', {'class': 'concall-link', 'target': '_blank', 'rel': 'noopener noreferrer'})
            rec = tag.find('a', {'class': 'concall-link', 'target': '_blank', 'rel': 'noopener noreferrer', 'href': True})
            concalls[name.text.strip()] = {
                'Transcript': transcript['href'] if transcript else None,
                'Notes': notes['data-url'] if notes else None,
                'PPT': ppt['href'] if ppt else None,
                'Recording': rec['href'] if rec else None
            }
        df = pd.DataFrame.from_dict(concalls, orient='index')
        return df