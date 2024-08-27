"""
    client for GearAPI
"""
import pandas as pd
from gear_api.exceptions import DeviceListFilteringError
from typing import Union,List
from gear_api.resource import events_resource, inventory_resource, measurements_resource
from gear_api.rest_adaptor import RestAdaptor
import os


class Client:
    """Client for Gear resource"""

    events = events_resource.EventsResource()
    inventory = inventory_resource.InventoryResource()
    measurements = measurements_resource.MeasurementsResource()

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)

        for name, resource in cls.__dict__.items():
            if isinstance(resource, RestAdaptor):
                resource_cls = type(resource)
                resource = resource_cls()
                setattr(self, name, resource)

        return self

    def __init__(
            self,
            device_list_path:str = 'device_list.csv',

    ) -> None:
        if os.path.exists(device_list_path):
            self.devices_list = pd.read_csv(device_list_path) 
        else:
            self.devices_list = self.inventory.get_devices_list()

        self.rest_adaptor = RestAdaptor()

    def download(
            self, 
            date_start:str, 
            date_end:str,
            output_file_path = 'output.csv', 
            device_params:dict = None, 
            OR_filtering = True,
            aggregate_period = None,
            **request_params,
            ) -> None:

        """
        downloads all the data from the gear api to a csv file.
        args:
            output_file_path - the path to the output file.
            date_start - the start date of the data to download. format YYYY-MM-DD
            date_end - the end date of the data to download. format YYYY-MM-DD
            device_params - a key-value filtering criteria for the devices. Uses the device_list columns as filtering criteria. 
            OR_filtering - greedy search for all filtering critieria. set to 0 for AND filtering.
            aggregate_period - the aggregation period for the measurements.
            request_params - an additional key-value filtering criteria to the request_params. See the resource class for more information.
        """
        total_devices,ids,resource_endpoint = self._filtered_devices_ids(
            device_params = device_params ,
              OR_filtering = OR_filtering)
        endpoints_ids = zip(ids,resource_endpoint)
        total_df = pd.DataFrame()

        for idx, (ids,resource_endpoint) in enumerate(endpoints_ids):
            if resource_endpoint == 'event/events' and aggregate_period:
                raise DeviceListFilteringError(f'ids {ids} is a event type data and does not provide aggregation. See device list for more information')

            if resource_endpoint == 'event/events':
                df,message = self.events.get_all_events(
                    id = ids, 
                    date_start= date_start, 
                    date_end= date_end,
                    **request_params
                    )
            elif resource_endpoint == 'measurement/measurements':
                if aggregate_period:

                    df,message = self.measurements.get_all_aggregated_measurements(
                        aggregate_period = aggregate_period,
                        id = ids, 
                        date_start= date_start, 
                        date_end= date_end,
                        **request_params
                    )
                else:
                    df,message = self.measurements.get_all_measurements(
                        id = ids, 
                        date_start= date_start, 
                        date_end= date_end,
                        **request_params
                    )
            try:
                total_df = pd.concat([total_df, df], axis=0)
            except UnboundLocalError:
                pass

            print(f"{idx + 1}/{total_devices} completed. {message}")
        
        total_df.to_csv(output_file_path, index=False)

    def post_setpoints(self, opc_code:str,value:float) -> None:
        """
        Change setpoints & control of the BMS devices via opc code.
        args:
            opc_code - the opc code of the device.
            value - the value to set the setpoint/control to.

        """
        self.measurements.post_setpoints(opc_code,value)

    def _filtered_devices_ids(
            self, 
            device_params:dict, 
            OR_filtering:bool = 1,
            ) -> Union[int,List[str],List[int]]:
        """
        To filter devices dataframe based on device_list_filter_params parameter and return back the ids. Case-insensitive
        note: supported_fragment filtering for multiple values uses OR method. (all the values mentioned will be included in the filtering)
        args:
            device_params - a key-value filtering criteria for the devices
            OR_filtering - greedy search for all filtering critieria. set to 0 for AND filtering.
        return:
            a list of device ids that met the filtering criteria
        """

        df = self.devices_list
        df.columns = df.columns.str.lower()
        df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        device_params = {k.lower(): v.lower() if isinstance(v, str) else v for k, v in device_params.items()}
        
        for key,val in device_params.items():

            if val in (None,[]):
                continue
            elif isinstance(val, list): 

                if OR_filtering:
                    if key == 'supported_fragment': #to handle dicts-like values for supported_fragment column.
                        filtered_df = pd.DataFrame()
                        for x in val:
                            x = str(x)
                            temp = df.loc[df[key].str.contains(x, na=False)]
                            filtered_df = pd.concat([filtered_df, temp], axis=0)

                        df = filtered_df
                        if len(df) == 0:
                            return DeviceListFilteringError()
                    else:
                        df = df.loc[df[key].isin(val)]
                else:
                    df = df[df[key].apply(lambda x: all(s in x for s in val))]

                if len(df) == 0:
                    raise DeviceListFilteringError()

                continue
            elif isinstance(val, (str,int)):
                if key == 'supported_fragment': #to handle dicts-like values for supported_fragment column.
                    df = df.loc[df[key].str.contains(val)]

                    if len(df) == 0:
                        raise DeviceListFilteringError()
                    continue
                
                df = df.loc[df[key] == val]
                
                if len(df) == 0:
                        raise DeviceListFilteringError()
            else:
                raise DeviceListFilteringError()

        check = df.loc[df['resource_endpoint'].isnull(),'id'].count()
        if check > 0:
            raise DeviceListFilteringError("Filtering criteria does not have a valid endpoint. Please check your criteria again")

        ids = df['id'].tolist()
        resource_endpoint = df['resource_endpoint'].tolist()

        total_devices = len(ids)

        if not ids:
            raise DeviceListFilteringError()
        
        return total_devices,ids,resource_endpoint
    
    def get_device_list_with_fragments(self) -> None:
        self.inventory.get_devices_list(with_fragment= True)
