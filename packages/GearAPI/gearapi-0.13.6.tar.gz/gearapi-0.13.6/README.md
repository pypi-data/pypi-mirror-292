This is a Python client for the Cumulocity Data API. The GearAPI package is a wrapper to simplify GET requests and JSON response parsing from the Measurement and Event Resources. 

This library abstracts:
1. API endpoint handling
2. pagnation handling
3. API retry
4. file handling
5. Handling API from multiple devices 

## how to use
1. setup a config.ini
```
[API]
USER = <IoT Platform User Name>
PASSWORD = <IoT Platform User Password>
BASE_URL = <IoT Platform Base URL>
TENANT_ID = <IoT Platform Tenant ID>

```

2. `pip install GearAPI`


```
import Client
client = Client()

date_start = "2024-01-01"
date_end = "2024-01-02"
device_params = {
    "devicetype": "iaq"
}
client.download(date_start, date_end, device_params)

"""
output: all the iaq devices data from 2024-01-01 to 2024-01-02
"""
```
