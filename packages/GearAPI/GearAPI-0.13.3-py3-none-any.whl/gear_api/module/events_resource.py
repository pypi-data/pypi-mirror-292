# coding: utf_8
import pandas as pd
from gear_api.module.rest_adapter import RestAdapter
from gear_api.utilis.utilis import remove_empty_params, validate_datetime_str
from gear_api.helpers.helpers import multiple_json_normalize


"""
TODO: create a method for POST BMS device setpoints
"""


class EventsResource(RestAdapter):

    """API Wrapper from ThingsCloud IoT Platform

    args:
        device_list_df = a dataframe of GEAR devices metadata. For filtering search and lookup purpose.
        device_list_filter_params = a dict to store the filtering criteria defined by user.
        request_filter_params = a dict to store the params for API.
        rest_adapter = A generic Rest API adapter. Use to get/del/post data from ThingsCloud API.
        filtered_ids = a list of ids from device_list_df after filtering. For fetching data.
        multiple_value_filtering_type - OR or AND
    
    """

    def __init__(
            self,
            ) -> None:
        
        super().__init__()
        self.resource = '/event/events'


    def get_all_events(self, id:str, date_start:str, date_end:str, **kwargs) -> pd.DataFrame:
        """
        return all Result data available as pandas dataframe.
        args:
            id - device id. see device_list.csv for reference.
            date_start - start date of measurement
            date_end - end date of measurment.
            kwargs - (optional params) e.g. type, valueFragmentSeries, valueFragmentType - https://www.cumulocity.com/api/core/#operation/getMeasurementCollectionResource
        """

        request_params ={
            'dateFrom': date_start,
            'dateTo': date_end,
            'currentPage': 1,
            'type': kwargs.get('type'), #don't use it for source only method
            'withTotalPages': None, #don't use it unncessary. Additional load to server.
            'pageSize': kwargs.get('pageSize') or 2000,
            'source': id,
            'revert': kwargs.get('revert'),
            'withSourceDevices': 'True',
            **kwargs

        }

        request_params = remove_empty_params(request_params)
        print(request_params)
        results_data = []
        while True:
            result = self.get(endpoint = self.resource, ep_params=request_params)
            result_data_events = result.data.get('events',None)
            print(result_data_events)
            if not result_data_events:
                break
            results_data.append(result_data_events)
            request_params['currentPage'] +=1

        df = multiple_json_normalize(results_data)
        return df

    


date_start = '2024-01-01'
date_end = '2024-08-11'

# datetime_post = '2024-04-01T00:11:22.000Z'
aa = EventsResource()
print(aa.get_all_events(541819, date_start, date_end))
# print(aa.get_all_aggregated_measurements('DAILY', 341512918, date_start, date_end))



# # coding: utf_8
# import requests
# from requests.auth import HTTPBasicAuth
# from requests.adapters import HTTPAdapter
# import json
# import pandas as pd
# from pandas import DataFrame
# from datetime import datetime,timedelta
# from src.utilis.logging import logger
# from src.utilis.path_utilis import config_dir,device_list_dir, stats_dir,downloads_dir, audit_dir
# import os
# from src.module.exceptions import DeviceFilePathError,DeviceListFilteringError,DeviceTypeError,SchemaChangeError
# from typing import List, Optional, Dict, Union, Generator, Tuple
# from src.utilis.models import *
# from dataclasses import dataclass,fields
# from src.module.rest_adapter import RestAdapter
# from src.utilis.utilis import remove_empty_params
# from src.helpers.helpers import download_file_handler, things_clouds_API_json_normalize

# class EventsResource():

#     """Event

#     args:
#         device_list_df = a dataframe of GEAR devices metadata. For filtering search and lookup purpose.
#         device_list_filter_params = a dict to store the filtering criteria defined by user.
#         request_filter_params = a dict to store the params for API.
#         rest_adapter = A generic Rest API adapter. Use to get/del/post data from ThingsCloud API.
#         filtered_ids = a list of ids from device_list_df after filtering. For fetching data.
    
#     """

#     def __init__(
#             self,
#             device_list_file_path:str,
#             device_list_filter_params:object = None,
#             request_filter_params:object = None,
#             value_fragment_type:str = None,
#             value_fragment_series:str = None,
#             device_ids:list = None
#             ) -> None:
        
#         self.device_list_df = self._set_device_list_df(device_list_file_path)
#         self.device_list_filter_params = device_list_filter_params
#         self.request_filter_params = request_filter_params
#         self.request_params = self._set_request_params()
#         self.rest_adapter = RestAdapter()
#         self.filtered_ids = device_ids or self._filtered_devices_ids()

#     def _set_request_params(self) -> None:
#         """
#         A general request params rule for rest adapter. To remove params if none is supplied by user.
#         """
#         if self.request_filter_params:
#             return { #params for java app
#             'dateFrom': self.request_filter_params.dateFrom,
#             'dateTo': self.request_filter_params.dateTo,
#             'currentPage': None,
#             'type': None, #don't use it for source only method
#             'withTotalPages': None, #don't use it unncessary. Additional load to server.
#             'pageSize': 2000,
#             'valueFragmentType': self.request_filter_params.valueFragmentType,
#             'valueFragmentSeries': self.request_filter_params.valueFragmentSeries,
#             'source': None,
#             'revert': None,
#             'withSourceDevices': 'True',
#             'aggregationType': self.request_filter_params.aggregationType.value
#             }
            
#         else:
#             return None
        
#     def _set_device_list_df(self, device_list_file_path) -> pd.DataFrame:
#         """
#         To set device list df based on filepath. To ensure supplied device list has proper columns.
#         """
#         try:
#             device_list_df = pd.read_csv(device_list_file_path)
#             return device_list_df
#         except FileNotFoundError as e:
#             logger.error(f"device list file not found. Check the path.")
#             exit()
        
#         if 'id' not in self.device_list_df.columns or 'type' not in self.device_list_df.columns:
#             logger.error(f"device list does not contain required information (id and type). Check your device list file")
#             exit()
    
#     def fetch_sensor_data(self, endpoint:str, params:dict = None, page_num:int = None, id:Union[int,str] = None) -> dict:

#         """

#         Return first page of the sensor-related values from thingscloud API.

#         args:
#             params - parameters for measurement/measurements API endpoint
#             page_num - page number parameters
#             id - device id parameter
#         """

#         if page_num is not None:
#             params['currentPage'] = page_num

#         if params:
#             params['source'] = id
#             params = remove_empty_params(params)
#             logger.debug(f"endpoint: {endpoint} param :{params}")

#         result = self.rest_adapter.get(endpoint = endpoint, ep_params = params)
#         sensor_data = result.data
#         return sensor_data

#     def _endpoint_router(self, id: Union[int,str]) -> str:
#         """
#         To get the endpoint of the id, based on their type. Things Cloud API requirement different endpoint set for measurement data or event data.
#         """
#         df = self.device_list_df
#         type_ = df.loc[df['id'] == int(id)]['endpointType'].item()

#         if type_ == '/measurement/measurements':
#             if self.request_params.get('aggregationType') is not None:
#                 return "/measurement/measurements/series"
#             return "/measurement/measurements"
#         elif type_ == "/event/events":
#             return "/event/events"
#         else:
#             raise ValueError('device list endpointType should only contain measurements or events endpoint')

#     def fetch_all_sensor_data(self, id: Union[int,str]) -> Tuple[str,list]:

#         """

#         Return specified period of the sensor-related values from thingscloud API based on device id.

#         args:
#             id - device id 
#         """
        
#         all_sensor_information = []
#         endpoint = self._endpoint_router(id)
#         page = 1

#         while True:
#             sensor_data = self.fetch_sensor_data(endpoint = endpoint, page_num = page,params=self.request_params, id = id)

#             data_type = {
#                 '/measurement/measurements' : 'measurements',
#                 '/event/events' : 'events',
#                 '/measurement/measurements/series' : ('values','series') #aggregation
#             }

#             data_type = data_type.get(endpoint)

#             sensor_information = sensor_data.get(data_type) if isinstance(data_type,str) else sensor_data

#             all_sensor_information.append(sensor_information) #append first to cater for values-type one-page data.

#             if sensor_information == [] or data_type == ('values','series'):
#                 break
            

#             page +=1

#         return data_type, all_sensor_information

#     def fetch_and_save_all_sensors_data(self) -> None:

#         """

#         Return specified period of the sensor-related values from thingscloud API based on device id.

#         args:
#             id - device id 
#         """

#         date_from = self.request_filter_params.dateFrom
#         date_to = self.request_filter_params.dateTo
#         date_now = datetime.now().strftime("%Y_%m_%d_%H%M%S")

#         for id in self.filtered_ids:

#             data_type, all_sensor_information = self.fetch_all_sensor_data(id)

#             df = things_clouds_API_json_normalize(data_type, all_sensor_information, id)
#             if len(df) > 0:
#                 file_path = download_file_handler(downloads_dir,  date_now, id, date_from, date_to)
#                 df.to_csv(file_path)
#             else:
#                 logger.info(f"no data found from {id}.")
        
#     def _filtered_devices_ids(self) -> Union[list,None]:
#         """
#         To filter devices dataframe based on device_list_filter_params parameter and return back the ids.
#         """
#         df = self.device_list_df

#         if not self.device_list_filter_params:
#             return None

#         for field in fields(self.device_list_filter_params):
#             value = getattr(self.device_list_filter_params, field.name)
#             if value == None:
#                 continue
#             df = df.loc[df[field.name] == value]
#             logger.info(f'{field.name} to filter: {value}\ndf row is {len(df)}')

#         ids_ = df['id'].to_list()
#         return ids_

#     def _safe_delete_measurements(delete_params: MeasurementDeleteParams) -> Result:
#         result = self.rest_adapter.delete(endpoint = '/measurement/measurements', ep_params = delete_params)
#         return result
    
#     #not ready
#     def _safe_bulk_delete_measurements(delete_params: BulkMeasurementDeleteParams) -> None:

#         #get source measurement data with the specified valueFragmenttype
#         #extract all the measurement id and stored it as set {}
#         #do a loop and feed each measuremnt id to the _safe_delete_measurements
#         # (optional)count how mnay successful delete based on the Result.status_code (between 200 to 299)
#         pass


    