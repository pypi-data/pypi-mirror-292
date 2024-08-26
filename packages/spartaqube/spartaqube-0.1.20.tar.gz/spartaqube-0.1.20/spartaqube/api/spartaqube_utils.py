import os
import base64
import json
import hashlib
import uuid
import requests
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
from decimal import Decimal
from datetime import datetime, date, time, timedelta

def is_scalar(input) -> bool:
    scalar_types = {
        int, str, float, bool, complex, type(None), bytes, bytearray,
        pd.Timestamp, pd.Timedelta, pd.Period, pd.Interval,
        pd.Categorical, pd.IntervalDtype, pd.CategoricalDtype,
        pd.SparseDtype, pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.Int64Dtype,
        pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype,
        pd.Float32Dtype, pd.Float64Dtype,
        pd.BooleanDtype, pd.StringDtype, pd.offsets.DateOffset,
        np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64,
        np.float16, np.float32, np.float64, np.complex64, np.complex128,
        np.bool_, np.bytes_, np.str_,
        datetime, date, time, timedelta,
        Decimal
    }
    
    return isinstance(input, tuple(scalar_types))
    
def process_scalar_args(args:list):
    '''
    Process scalar -> list for polymorphism
    '''
    def process_dataframe(df):
        cols = df.columns
        len_col = len(cols)
        if len_col >= 1:
            return [df[col] for col in cols] # list of series
        return df

    def process_scalar_list(input):
        if input is not None:
            if input.__class__.__name__.lower() == 'ndarray': # Convert to dataframe first if ndarray
                input = pd.DataFrame(input)
            
            if isinstance(input, pd.Series):
                return [input]
            if isinstance(input, pd.DataFrame):
                return process_dataframe(input)
            if isinstance(input, pd.DatetimeIndex):
                return [input.tolist()]
            if isinstance(input, pd.core.indexes.base.Index):
                return input.tolist()
            
            if len(input) > 0:
                if is_scalar(input[0]):
                    return [input]
                
                # If list of dataframes:
                if all(isinstance(df, pd.DataFrame) for df in input):
                    merged_df = pd.concat(input, axis=1)
                    return process_dataframe(merged_df)
                
                # If list of ndarray:
                if all(df.__class__.__name__.lower() == 'ndarray' for df in input):
                    input = [pd.DataFrame(df) for df in input]
                    merged_df = pd.concat(input, axis=1)
                    merged_df.columns = [f'Y{i+1}' for i in range(len(input))]
                    return process_dataframe(merged_df)
                
        return input
    
    args_to_scalar_process = ['x', 'y', 'r', 'datalabels', 'border', 'background', 'tooltips', 'border_style']
    for this_arg in args_to_scalar_process:
        try:
            args[this_arg] = process_scalar_list(args[this_arg])
        except:
            pass

    if 'ohlcv' in args:
        if isinstance(args['ohlcv'], pd.DataFrame):
            this_df = args['ohlcv']
            args['ohlcv'] = [this_df[col] for col in this_df.columns]

def get_ws_settings(api_key:str) -> list:
    return (Fernet(get_keygen_fernet().encode('utf-8'))).decrypt(base64.b64decode(api_key)).decode('utf-8').split('@')[1:]

def get_keygen_fernet() -> str:
    return base64.b64encode(hashlib.md5('spartaqube-api-key'.encode('utf-8')).hexdigest().encode('utf-8')).decode('utf-8')

def request_service(spartaqube_api_intance, service_name:str, data_dict:dict) -> dict:
    '''
    Web service request
    '''
    data_dict['api_service'] = service_name
    json_data_params = {
        'jsonData': json.dumps(data_dict)
    }
    headers = {
        "Content-Type": "application/json"
    }
    url = f"{spartaqube_api_intance.domain_or_ip}/api_web_service"
    res_req = requests.post(url, json=json_data_params, headers=headers)
    status_code = res_req.status_code
    if status_code != 200:
        print(f"An error occurred, status_code: {status_code}")
        return {
            'res': -1,
            'status_code': status_code,
        }

    return json.loads(res_req.text)

def upload_resources(spartaqube_api_intance, data_dict:dict, file_path:str) -> dict:
    '''
    Upload resources (file or folder)
    '''

    def upload_func(files):
        json_data_params = {
            'jsonData': json.dumps(data_dict)
        }
        headers = {
            "Content-Type": "application/json"
        }
        url = f"{spartaqube_api_intance.domain_or_ip}:{spartaqube_api_intance.http_port}/api_web_service"
        # print("url  > "+str(url))
        res_req = requests.post(url, json=json_data_params, headers=headers, files=files)
        status_code = res_req.status_code
        if status_code != 200:
            print(f"An error occurred, status_code: {status_code}")
            return {
                'res': -1,
                'status_code': status_code,
            }

        return json.loads(res_req.text)
    
    data_dict['api_service'] = 'upload'
    is_file = False
    if os.path.isfile(file_path):
        is_file = True

    if is_file:
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        files = {'file': (f"{file_name}.{file_extension}", open(file_path, 'rb'))}
        return upload_func(files)
    else: # We are dealing with a folder, we are going to recursively upload each file
        pass
    