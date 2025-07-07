import json
import brotli
from requests import Session, session
from requests.adapters import HTTPAdapter, Retry


class CustomSession:
    """
        A custom class for creating a session object with retries, timeouts, and headers.

        Attributes:
            session : session object for making HTTP requests
            headers: headers required for getting data from a website via API

        Methods:
            __init__(self, headers: dict = None) -> None:
                Initializes the CustomSession object with the given headers.

            get_session(self) -> Session:
                Returns the session object.

            hit_and_get_data(self, url: str, params: dict = None) -> dict:
                Hits the API and gets the data based on the endpoint and parameters passed.

        Args:
            headers : (optional) headers required for getting data from a website via API

        Returns:
            dict : JSON parsed result of the output response data from the API

        Raises:
            JSONDecodeError : If there is an error in decoding the JSON response
            Exception: If there is an error in connecting to the URL
    """

    def __init__(self, headers: dict = None) -> None:
        """
            It's a custom class that does the common functionalities creating a session object with Retries, timeouts,
            builds from the headers, etc.

            :param self: Represent the instance of the class
            :param headers: (optional) headers required for getting data from a website via api. This is required
             because most of the websites require headers since they validate few to identify it is genuinely used

            :return: None
        """

        self.session = session()
        if headers:
            self.headers = headers
        else:
            self.headers = {}

        retries = Retry(total=3,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504, 400, 401, 402, 403])

        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.timeout = 30  # timeout for 30 seconds

    def get_session(self) -> Session:
        """
            This functions returns the session object which is built when a class object being constructed.

            :param self: Represent the instance of the class

            :return: Session object of the class
        """

        return self.session

    def hit_and_get_data(self, url: str, params: dict = None) -> dict:
        """
            Hitting the api and gets the data based on the endpoint passed as well as the url params / params for the
            get type of requests, all api used in this library are of get type so its supports only GET type requests

            :param self: Represent the instance of the class.
            :param url: Endpoint of the api; aka link of the api
            :param params: (optional) parameters which is required to get exact data from the api aka url params

            :return: Dict object which is json parsed result of the output response data got from hitting above request
        """

        try:
            if params:
                response =  self.session.get(url, params=params, headers=self.headers)
            else:
                response =  self.session.get(url, headers=self.headers)
            encoding = response.headers.get('Content-Encoding', '')
            if encoding == 'br':
                try:
                    data = brotli.decompress(response.content).decode("utf-8")
                except brotli.error:
                    data = response.content.decode("utf-8")
            else:
                data = response.text
            return json.loads(data)
        except json.JSONDecodeError:
            return {}
        except Exception as err:
            print(f'Error in connecting to url : {url} Error : {err}')
            return {}

