# coding: utf_8

import requests
from requests.auth import HTTPBasicAuth
from json import JSONDecodeError
from gear_api.models.rest_adapter_models import Result
from gear_api.utilis.utilis import retry
from gear_api.module.exceptions import RequestError
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

class RestAdapter:
    """
    A Generic RestAdaptor. To get/post/del data from API

    args:
        _credentials = a stored credential from config.ini. Use for API authentication.
        _ssl_verify = a generic ssl verification. (Not required for things Cloud API call.)
    """

    def __post_init__(self):
        self.user = config.get('API', 'USER')
        self.password = config.get('API', 'PASSWORD')

    def __init__(self, ssl_verify: bool = True):
        self.base_url = 'https://thegear.jp.cumulocity.com'
        self.tenant_id = 't21092648'
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            # noinspection PyUnresolvedReferences
            requests.packages.urllib3.disable_warnings()
        self.__post_init__()
    
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
        return paginated Result.
        """
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params)

    def post(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        return self._do(http_method='POST', endpoint=endpoint, ep_params=ep_params, data=data)

    def delete(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        return self._do(http_method='DELETE', endpoint=endpoint, ep_params=ep_params, data=data)

