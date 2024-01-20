from datetime import datetime
from os import makedirs
from Base import CustomSession


class BSE(CustomSession):

    def __init__(self):
        """
            The __init__ function is called when the class is instantiated.
            It sets up the instance of the class, and it's where you put all your initialization code.


            Args:
                self: Represent the instance of the class

            Returns:
                An object of the class bse
        """
        super().__init__(headers={
            'authority': 'api.bseindia.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'origin': 'https://www.bseindia.com',
            'referer': 'https://www.bseindia.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        })

        self._base_url = 'https://api.bseindia.com/BseIndiaAPI/api/'

    def download_annual_reports(self, bse_code: str, from_year: str = None, to_year: str = str(datetime.now().year), folder_path: str = '.'):
        """
            The download_annual_reports function downloads the annual reports of a company from BSE India website.

            Args:
                self: Represent the instance of the class
                bse_code: str: Specify the company's bse code.
                from_year: str: Specify the year from which we want to download annual reports.
                to_year: str: Specify the year to which the annual reports should be downloaded.
                folder_path: str: Specify the path where the annual reports will be downloaded Note: New folder will
                be created within this folder with name `bse_code`.

            Returns:
                None But downloads the annual reports of the company and saves into a new folder in the specified
                path with a folder named `bse_code` which contains `year.pdf` files
        """
        folder_path = f"{folder_path}/{bse_code}"
        makedirs(folder_path, exist_ok=True)

        params = {
            'scripcode': bse_code,
        }

        if from_year is None:
            from_year = '0000'

        response = self.session.get('https://api.bseindia.com/BseIndiaAPI/api/AnnualReport_New/w',
                                    params=params,
                                    headers=self.headers).json()

        for yr in response.get('Table', []):
            link = yr.get('PDFDownload', '')
            year = yr.get('Year')
            if year < from_year or year > to_year:
                continue
            pdf_data = self.session.get(link, headers=self.headers)
            with open(f'{folder_path}/{year}.pdf', 'wb') as pdf_file:
                pdf_file.write(pdf_data.content)
