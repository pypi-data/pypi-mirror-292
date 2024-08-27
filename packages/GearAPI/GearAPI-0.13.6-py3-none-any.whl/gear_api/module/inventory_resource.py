# coding: utf_8
import pandas as pd
from gear_api.module.rest_adapter import RestAdapter
from datetime import datetime


class InventoryResource(RestAdapter):

    def __init__(self):
        super().__init__()

    def get_device_count(self, query=None):
        """get the total number of devices

        Args:
            base_uri(string): Base URI of the connection destination
            user(string): Username for authentication
            password(string): Password for authentication
            query(string): Query for filtering(optional)

        Returns:
            integer: number of devices

        """
        resource = '/inventory/managedObjects'
        params = {
            'pageSize': 1,
            'withTotalPages': 'true'
        }
        if query is not None:
            params['query'] = query
        res = self.get(endpoint = resource, ep_params=params)
        device_count = res.data['statistics']['totalPages']
        return device_count

    def get_devices_info(self, query=None) -> pd.DataFrame:
        """get information of all devices
        
        Args:
            base_uri(string): Base URI of the connection destination
            user(string): Username for authentication
            password(string): Password for authentication

        Returns:
            dataframe: Pandas DataFrame containing device information

        """
        total_pages = self.get_device_count()
        resource = '/inventory/managedObjects'
        params = {
            'pageSize': 2000,
            'query': query or "has(c8y_Availability)" #remove non-device object by default unless new query provided.
        }
        if query is not None:
            params['query'] = query
        results = []
        for current_page in range(1,total_pages+1):
            params['currentPage'] = current_page
            res = self.get(endpoint = resource, ep_params=params)
            data = res.data
            if len(data['managedObjects']) == 0:
                break
            else:
                for managed_object in data['managedObjects']:
                    # temp_dict is just sample.
                    # you can add keys for the desired attribute information to this dictionary.
                    temp_dict = {
                        'id': managed_object.get('id', ''),
                        'name': managed_object.get('name', ''),
                        'deviceType': managed_object.get('deviceType', '').lower(),
                        'subType': managed_object.get('subType', '').lower(),
                        'status': managed_object.get('c8y_Availability', {}).get('status', ''),
                        'lastMessage': managed_object.get('c8y_Availability', {}).get('lastMessage', ''),
                        'zid': managed_object.get('zid', ''),
                        'zoneName': managed_object.get('zoneName', ''),
                        'floor': managed_object.get('floor', '').lower(),
                        'type': managed_object.get('type', '').lower(),
                        'owner': managed_object.get('owner', ''),
                        # 'resource_endpoint': (
                        #                 '/event/events' if managed_object.get('type', '') in endpoint_type['events'] 
                        #                 else '/measurement/measurements' if managed_object.get('type', '') in endpoint_type['measurements'] 
                        #                 else ''
                        #                     )
                    }
                    results.append(temp_dict)
        df = pd.DataFrame(results)
        return df
    
    def get_supported_fragment(self,df:pd.DataFrame) -> pd.DataFrame:
        """
        Retrieve all supported measurement fragments and series of a specific managed object by a given ID. 
        Useful as reference to work with specific measurement fragment.
        args:
            df - df generated from get_device_info
        return:
            df with supported fragment column.
        """

        for id in df['id']:
            resource = f'/inventory/managedObjects/{id}/supportedMeasurements'
            result = self.get(endpoint = resource)
            supported_fragment = result.data
            df.at[df['id'] == id, 'supported_fragment'] = [supported_fragment]

        return df


    def get_supported_fragment_and_series(self,df:pd.DataFrame) -> pd.DataFrame:
        """
        Retrieve all supported measurement fragments and series of a specific managed object by a given ID.
        Useful as reference to work with specific measurement fragment and series.
        args:
            df - df generated from get_device_info
        """
        
        for id in df['id']:
            resource = f'/inventory/managedObjects/{id}/supportedSeries'
            result = self.get(endpoint = resource)
            supported_fragment = result.data
            print(f"ID: {id}, Supported Fragment: {supported_fragment}")
            df.at[df['id'] == id, 'supported_fragment'] = [supported_fragment]

        return df

    def _get_endpoint(self,df:pd.DataFrame) -> pd.DataFrame:
        """
        Set event resource or measurements resource endpoint for each devices in the df. 
        This will allow GET request to go to the correct endpoint and retrieve the data.
        args:
            df - df generated from get_device_info
        return:
            df with a new column (resource_endpoint) that has the resource endpoint
        """

        events_endpoint = ('cctv','acms','vms','ai-camera','pms','smart_box')
        measurements_endpoint = ('iaq','smart_landscaping','restroom','solar_panel','BMS','LMS')

        #collabo devices contain measurements and event type. This method is not robust due to type column is frequently populated. TODO: find alternative to query check collabo endpoint
        collabo_events_endpoint = ('ktg_tabletuser','ktg_fisheye_camera','ktg_dome_camera','ktg_conversation_sensor','ktg_bicycle_load','ktg_tablet_screen')
        collabo_measurements_endpoint = ("ktg_tablet", "ktg_mic_array", "ktg_humidification", "ktg_aq_illuminance", "ktg_diffuseron", "ktg_illuminance_Uv", "ktg_spot_light", "ktg_illuminance_I", "ktg_airflow", "ktg_controller_table", "ktg_camera", "ktg_fan", "ktg_ventilation", "ktg_ziaino", "ktg_aircon", "ktg_pillar_light", "ktg_meeting", "ktg_air_quality_H", "ktg_dehumidification", "ktg_air_quality_T", "ktg_space_player", "ktg_speaker", "ktg_line_light", "ktg_scene", "ktg_actuation_trigger", "ktg_ventilation_fan", "ktg_humidification_fan", "utilization_rate", "fine_mist_machine_(green_aircon)", "uilization_rate")
        
        df.loc[df['deviceType'].isin(events_endpoint), 'resource_endpoint'] = 'event/events'
        df.loc[df['deviceType'].isin(measurements_endpoint), 'resource_endpoint'] = 'measurement/measurements'
        df.loc[df['type'].isin(collabo_events_endpoint), 'resource_endpoint'] = 'event/events'
        df.loc[df['type'].isin(collabo_measurements_endpoint), 'resource_endpoint'] = 'measurement/measurements'

        return df
    
    def get_enhanced_devices_info(self) -> pd.DataFrame:
        """
        Enhance the device info list with 2 additional columns.
        
        args:
            df - df generated from get_device_info
        return:
            df with 2 new columns (resource_endpoint and supported_fragment)
        """
        df = self.get_devices_info(query=None)
        df = self.get_supported_fragment_and_series(df)
        df = self._get_endpoint(df)
        df['device_list_query_date'] = datetime.today()
        return df
