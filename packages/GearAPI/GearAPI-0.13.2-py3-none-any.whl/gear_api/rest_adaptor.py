# coding: utf_8

import logging.config
import requests
from requests.auth import HTTPBasicAuth
from json import JSONDecodeError
from gear_api.models.rest_adaptor_models import Result
from gear_api.utilis.utilis import retry
from gear_api.exceptions import RequestError
import configparser
from typing import Dict
import os
import logging
from gear_api.helpers.helpers import validate_date

# Configure logging at the module level
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='API.log',  # Log output file
    filemode='w'  # Write mode (overwrite)
)

logger = logging.getLogger(__name__)


class RestAdaptor:
    """
    A Generic Rest Adaptor with credential.

    args:
        _credentials = a stored credential from config.ini. Use for API authentication.
        _ssl_verify = a generic ssl verification. (Not required for things Cloud API call.)
    """

        
    def __init__(self, ssl_verify: bool = True):
        self.config = configparser.ConfigParser()
        try:
            self.config.read(os.path.join(os.path.dirname(__file__), 'config.ini')) #look for config.ini in the same dir as this file
        except configparser.NoSectionError:
            self.config.read('config.ini') #look for config.ini in current working dir

        self.user = self.config.get('API', 'USER')
        self.password = self.config.get('API', 'PASSWORD')
        self.base_url = self.config.get('API', 'BASE_URL')
        self.tenant_id = self.config.get('API', 'TENANT_ID')
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            # noinspection PyUnresolvedReferences
            requests.packages.urllib3.disable_warnings()
    
    @retry(attempts=3, delay=2, backoff=2)
    def _do(self, http_method: str, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        """
        A generic rest API call method
        args:
            http_method = http method. e.g get, post, del
            endpoint = endpoint of the request url.
            ep_params = endpoint params for the request url.
            data = data to perform POST method.
        output:
            Result = An API data wrapped in a object class with additional meta information of the API request. 
        """
        full_url = self.base_url + endpoint

        if ep_params:
            validate_date(ep_params.get('dateTo'))
            validate_date(ep_params.get('dateFrom'))
        
        #logger.debug(ep_params)
        try:
            response = requests.request(method=http_method, url=full_url, verify=self._ssl_verify,
                                        auth=HTTPBasicAuth(self.user, self.password), params=ep_params, json=data)
        except requests.exceptions.RequestException as e:
            raise RequestError("Request failed") from e
        try:
            data_out = response.json()
        except (ValueError, JSONDecodeError) as e:
            raise RequestError("Bad JSON in response") from e
        if 299 >= response.status_code >= 200:     # 200 to 299 is OK
            return Result(response.status_code, message=response.reason, data=data_out)

        raise RequestError(f"{response.status_code}: {response.reason}")

    def get(self, endpoint: str, ep_params: Dict = None) -> Result:
        """
        Generic REST GET method.
        args:
            endpoint - endpoint of the request url.
            ep_params - endpoint params for the request url.
        return:
            Result = An API data wrapped in a object class with additional meta information of the API request. 
        """
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params)

    def post(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        """
        Generic REST POST method.
        args:
            endpoint - endpoint of the request url.
            ep_params - endpoint params for the request url.
            data - data to perform POST method.
        return:
            Result = An API data wrapped in a object class with additional meta information of the API request. 
        """
        return self._do(http_method='POST', endpoint=endpoint, ep_params=ep_params, data=data)

    def delete(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        """
        Generic REST DELETE method.
        args:
            endpoint - endpoint of the request url.
            ep_params - endpoint params for the request url.
            data - data to perform DELETE method.
        return:
            Result = An API data wrapped in a object class with additional meta information of the API request. 
        """
        return self._do(http_method='DELETE', endpoint=endpoint, ep_params=ep_params, data=data)

