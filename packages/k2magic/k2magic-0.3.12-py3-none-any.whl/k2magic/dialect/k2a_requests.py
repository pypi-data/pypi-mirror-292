import json

import requests

from k2magic.dataframe_db_exception import DataFrameDBException


def get(url, auth, tenant: str = None) -> json:
    headers = {}
    if tenant:
        headers = {'tenant': tenant}
    response = requests.get(url, auth=auth, verify=False, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        raise DataFrameDBException(f"{response.status_code} 业务错误 {url}: {response.json().get('message')}")
    elif response.status_code == 401:
        raise DataFrameDBException(f"{response.status_code} 认证错误 {url}: {response.json().get('message')}")
    elif response.status_code == 403:
        raise DataFrameDBException(f"{response.status_code} 认证错误 {url}: {response.json().get('message')}")
    elif response.status_code == 500:
        raise DataFrameDBException(f"{response.status_code} 服务器内部错误 {url}")
    else:
        raise DataFrameDBException(f"{response.status_code} Failed to fetch from {url}")


def get_stream(url, auth, tenant: str = None):
    headers = {}
    if tenant:
        headers = {'tenant': tenant}
    response = requests.get(url, auth=auth, verify=False, headers=headers, stream=True)
    if response.status_code == 200:
        # response.raise_for_status()
        return response
    elif response.status_code == 400:
        raise DataFrameDBException(f"{response.status_code} 业务错误 {url}: {response.json().get('message')}")
    elif response.status_code == 401:
        raise DataFrameDBException(f"{response.status_code} 认证错误 {url}: {response.json().get('message')}")
    elif response.status_code == 403:
        raise DataFrameDBException(f"{response.status_code} 认证错误 {url}: {response.json().get('message')}")
    elif response.status_code == 500:
        raise DataFrameDBException(f"{response.status_code} 服务器内部错误 {url}")
    else:
        raise DataFrameDBException(f"{response.status_code} Failed to fetch from {url}")

