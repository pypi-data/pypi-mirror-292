import pandas as pd
from gear_api.module.exceptions import DeviceListFilteringError

def filtered_devices_ids(device_list_path:str, device_params:dict) -> list:
        """
        To filter devices dataframe based on device_list_filter_params parameter and return back the ids.
        note: supported_fragment filtering for multiple values uses OR method. (all the values mentioned will be included in the filtering)
        args:
            device_params - a key-value filtering criteria for the devices
        return:
            a list of device ids that met the filtering criteria
        """

        df = pd.read_csv(device_list_path)

        multiple_value_filtering_type = device_params.pop('multiple_value_filtering_type', None)
        multiple_value_filtering_type = multiple_value_filtering_type.lower()
        print(multiple_value_filtering_type)

        if not device_params:
            ids = df['id'].tolist()
            return ids

        for key,val in device_params.items():
            key = key.lower()
            
            if val == None:
                continue
            elif isinstance(val, list): 

                if multiple_value_filtering_type == 'or':
                    if key == 'supported_fragment': #to handle dicts-like values for supported_fragment column.
                        filtered_df = pd.DataFrame()
                        for x in val:
                            print(x)
                            x = str(x)
                            temp = df.loc[df[key].str.contains(x, na=False)]
                            filtered_df = pd.concat([filtered_df, temp], axis=0)
                            print('temp',len(temp))

                        df = filtered_df
                        if len(df) == 0:
                            return DeviceListFilteringError()
                    else:
                        val = [x.lower() for x in val]
                        df = df.loc[df[key].isin(val)]
                elif multiple_value_filtering_type == 'and':
                    df = df[df[key].apply(lambda x: all(s in x for s in val))]
                else:
                    return DeviceListFilteringError("use OR or AND for multiple_value_filtering_type only")
                
                continue
            elif isinstance(val, (str,int)):
                if key == 'supported_fragment': #to handle dicts-like values for supported_fragment column.
                    df = df.loc[df[key].str.contains(val)]
                    continue
                
                val.lower()
                df = df.loc[df[key] == val]
            else:
                return DeviceListFilteringError()

            print(f"rows left {len(df)}")

        ids = df['id'].tolist()

        print(len(ids))

        if not ids:
            return DeviceListFilteringError()
        return ids


# params = {
# # 'supported_fragment' : 'af_ll_sp.a',
# 'type' : ['cctv_wv-u2532la','fr_door_access'],
# 'multiple_value_filtering_type' : 'OR'
# }

# aa = filtered_devices_ids(device_list_path = '/home/darius/get_data/src/resources/device_list.csv', 
#                           device_params=params)

