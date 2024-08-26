import pandas as pd
from gear_api.module.rest_adapter import RestAdapter
from gear_api.utilis.utilis import remove_empty_params, validate_datetime_str
from gear_api.helpers.helpers import multiple_json_normalize


"""
TODO: create a method for POST BMS device setpoints
"""


class MeasurementsResource(RestAdapter):

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
        self.resource = '/measurement/measurements'


    def get_all_measurements(self, id:str, date_start:str, date_end:str, **kwargs) -> pd.DataFrame:
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
            'valueFragmentType': kwargs.get('valueFragmentType'),
            'valueFragmentSeries': kwargs.get('valueFragmentSeries'),
            'source': id,
            'revert': kwargs.get('revert'),
            'withSourceDevices': 'True',
            **kwargs

        }

        request_params = remove_empty_params(request_params)

        results_data = []
        while True:
            result = self.get(endpoint = self.resource, ep_params=request_params)
            result_data_measurements = result.data.get('measurements',None)
            if not result_data_measurements:
                break
            results_data.append(result_data_measurements)
            request_params['currentPage'] +=1

        df = multiple_json_normalize(results_data)
        return df

    def get_all_aggregated_measurements(self, aggregation_type:str, id:str, date_start:str, date_end:str, **kwargs) -> pd.DataFrame:
        """
        return all min max value of the aggregated period data as pandas dataframe. result will provide up to 5000 values. Reduce the date range if required.
        args:
            id - device id. see device_list.csv for reference.
            aggregation_type - aggregation period for the data. Accept "DAILY" "HOURLY" "MINUTELY"
            date_start - start date of measurement
            date_end - end date of measurment.
            kwargs - (optional params) e.g. type, valueFragmentSeries, valueFragmentType - https://www.cumulocity.com/api/core/#operation/getMeasurementCollectionResource
        """

        request_params ={
            'aggregationType': aggregation_type,
            'dateFrom': date_start,
            'dateTo': date_end,
            'type': kwargs.get('type'), #don't use it for source only method
            'series': kwargs.get('valueFragmentSeries'),
            'source': id,
            'revert': kwargs.get('revert'),
            **kwargs

        }
        page_num = request_params.get('currentPage')
        resource = self.resource + '/series'

        request_params = remove_empty_params(request_params)
        result = self.get(endpoint = resource, ep_params=request_params)
        results_data = result.data

        df = multiple_json_normalize(results_data, id, aggregated=True)

        if len(df) == 5000:
            print('data provided might have been trancated. Reduce the date range of the query')
            
        return df
    
    # def post_measurement(self, id:int,datetime:str,type:str, fragment_type:str = None, **custom_fragments) -> str:
    #     """
    #     post measurement data
    #     args:
    #         id - device id. see device_list.csv for reference.
    #         time - date and time of the device. format: YYYY-MM-DDTHH:MM:SS.sssZ
    #         type - device measurement type. see device_list.csv for reference. Note: if its a new fragment type, append c8y_ to avoid name conflict. (e.g. c8y_powermeter)
    #         fragment_type - fragment type.  e.g. kwh (fragment) or kwh.k (fragment and series). Note: if its a new fragment type, append c8y_ to avoid name conflict. (e.g. c8y_temperature)

    #     Note: Performance consideration. add

    #     return:
    #         return a Result Object that contains:
    #             message - indication whether its successful.
    #             data - data that is posted.
    #             status code - message status code
    #     """

        
    #     validate_datetime_str(datetime)

    #     ep_params = {

    #         'source' : id,
    #         'time' : datetime,
    #         'type': type,
    #         'c8y_Steam': fragment_type,
    #         **custom_fragments
    #     }

    #     ep_params = remove_empty_params(ep_params)
    #     print(ep_params)
    #     result = self.post(endpoint = self.resource, ep_params=ep_params)
    #     print(result.message)
    #     return result.__dict__

    # def remove_measurement(self, measurement_id:int) -> str:
    #     """
    #     remove measurement data
    #     args:
    #         measurement_id - measurement id is the Unique identifier of the measurement

    #     return:
    #         return a Result Object that contains:
    #             message - indication whether its successful.
    #             data - data that is deleted.
    #             status code - message status code       
    #     """
    #     ep_params = {
    #         "id" : measurement_id 
    #     }
    #     result = self.delete(endpoint = self.resource, ep_params=ep_params)

    #     print(result.message)
    #     return result.__dict__


# date_start = '2024-02-01'
# date_end = '2024-04-11'

# datetime_post = '2024-04-01T00:11:22.000Z'
# aa = MeasurementsResource()
#print(aa.get_all_measurements(191513041, date_start, date_end))
#print(aa.get_all_aggregated_measurements('DAILY', 341512918, date_start, date_end))
