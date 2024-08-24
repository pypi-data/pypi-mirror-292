import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import datetime
from sovai.errors.sovai_errors import InvalidCredentialsError

import requests
from sovai.api_config import ApiConfig

# Try to import CustomDataFrame, use regular DataFrame if not available
try:
    from sovai.extensions.pandas_extensions import CustomDataFrame
    HAS_CUSTOM_DATAFRAME = True
except ImportError:
    HAS_CUSTOM_DATAFRAME = False
    CustomDataFrame = pd.DataFrame  # Fallback to regular DataFrame


def verify_token(verbose=False):
    url = f"{ApiConfig.base_url}/verify/token/{ApiConfig.token}"  # Updated endpoint
    try:
        response = requests.get(url, verify=ApiConfig.verify_ssl)
        if verbose:
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            is_valid = result.get("is_valid", False)
            message = result.get("message", "No message provided")
            user_id = result.get("user_id")  # New field from the updated endpoint
            
            if verbose:
                print(f"Token verification result: {is_valid}")
                print(f"Message: {message}")
                if user_id:
                    print(f"User ID: {user_id}")
            
            return is_valid, user_id if user_id else None  # Return both validity and user_id
        else:
            if verbose:
                print(f"Unexpected response: {response.status_code} - {response.text}")
            return False, None
    except requests.RequestException as e:
        if verbose:
            print(f"Request failed: {e}")
        return False, None

# Usage


def load_parquet_file(url, columns=None, filters=None):
    """Load a single Parquet file from a public URL."""
    try:
        df = pd.read_parquet(url, columns=columns, filters=filters)
        return df
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return pd.DataFrame()


def get_file_url(base_url, ticker, name_file):
    """Construct the URL for the Parquet file of a specific ticker."""
    encoded_ticker = quote(ticker)
    return f"{base_url}/ticker={encoded_ticker}/{name_file}"


def get_file_url_partitioned(base_url, ticker, name_file):
    """Construct the URL for the Parquet file of a specific ticker using the first two letters partitioning."""
    first_two_letters = ticker[:2].upper() if ticker[:2].isalpha() else "0"
    return f"{base_url}/first_two_letters={first_two_letters}/{name_file}"


def load_data_for_ticker(
    base_url, ticker, columns, from_date, to_date, name_file, partitioned=False
):
    """Load data for a single ticker."""
    if partitioned:
        file_url = get_file_url_partitioned(base_url, ticker, name_file)
    else:
        file_url = get_file_url(base_url, ticker, name_file)

    filters = None
    if from_date is not None and to_date is not None:
        filters = [("date", ">=", from_date), ("date", "<=", to_date)]
    elif from_date is not None:
        filters = [("date", ">=", from_date)]
    elif to_date is not None:
        filters = [("date", "<=", to_date)]

    df = load_parquet_file(file_url, columns, filters)

    if isinstance(df.index, pd.MultiIndex) and "ticker" in df.index.names:
        df = df.reset_index()

    if partitioned:
        # Filter the DataFrame by the specific ticker
        df = df[df["ticker"] == ticker]

    df["ticker"] = ticker  # Add ticker column

    return df


def load_data_for_tickers(
    base_url, tickers, columns, from_date, to_date, name_file, partitioned=False
):
    """Load data for multiple tickers using concurrent.futures."""
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                load_data_for_ticker,
                base_url,
                ticker,
                columns,
                from_date,
                to_date,
                name_file,
                partitioned,
            )
            for ticker in tickers
        ]
        results = [future.result() for future in futures]

    # Concatenate DataFrames
    combined_df = pd.concat(results)
    # print(combined_df.head())
    combined_df.set_index(["ticker", "date"], inplace=True)

    return combined_df.sort_index()




def client_side_frame(endpoint, tickers, columns, start_date, end_date):
    is_valid, user_id = verify_token(verbose=False)

    if not is_valid:
        raise InvalidCredentialsError("Invalid or expired token. Please authenticate.")

    endpoint_config = {
        "ratios/relative": {
            "url": "https://storage.googleapis.com/sovai-partitioned/sovai-accounting/processed/ratios_percentile_weekly.parq",
            "name": "ratios_percentile_weekly_0.parquet",
            "partitioned": False,
        },
        "market/prices": {
            "url": "https://storage.googleapis.com/sovai-partitioned/sovai-accounting/prices.parq",
            "name": "prices_0.parquet",
            "partitioned": False,
        },
        "market/closeadj": {
            "url": "https://storage.googleapis.com/sovai-partitioned/sovai-accounting/prices_closeadj.parq",
            "name": "prices_closeadj_0.parquet",
            "partitioned": False,
        },
        "complaints/public": {
            "url": "https://storage.googleapis.com/sovai-partitioned/sovai-complaints/processed/consumer_complaint_public.parq",
            "name": "consumer_complaint_0.parquet",
            "partitioned": False,
        },
        "complaints/private": {
            "url": "https://storage.googleapis.com/sovai-partitioned/sovai-complaints/processed/consumer_complaint_private.parq",
            "name": "consumer_complaint_0.parquet",
            "partitioned": False,
        },
        "lobbying/public": {
            "url": "https://storage.googleapis.com/sovai-partitioned/sovai-lobbying/processed/lobbying_public.parq",
            "name": "lobbying_public_0.parquet",
            "partitioned": True,
        },
        "short/volume": {
            "url": "https://storage.googleapis.com/sovai-partitioned/sovai-short/processed/short_volume_weekly.parq",
            "name": "short_volume_weekly_0.parquet",
            "partitioned": True,
        },
    }

    if endpoint not in endpoint_config:
        raise ValueError(f"Invalid endpoint: {endpoint}")

    config = endpoint_config[endpoint]
    base_url = config["url"]
    name_file = config["name"]
    partitioned = config["partitioned"]

    # Load data
    df_percentiles = load_data_for_tickers(
        base_url, tickers, columns, start_date, end_date, name_file, partitioned
    )
    
    if HAS_CUSTOM_DATAFRAME:
        return CustomDataFrame(df_percentiles)
    else:
        return df_percentiles  # Returns a regular pandas DataFrame if CustomDataFrame is not available
    

# def client_side_frame(endpoint, tickers, columns, start_date, end_date):

#     is_valid, user_id = verify_token(verbose=False)

#     if not is_valid:
#         # print('invalid')
#         raise InvalidCredentialsError("Invalid or expired token. Please authenticate.")

#     endpoint_config = {
#         "ratios/relative": {
#             "url": "https://storage.googleapis.com/sovai-partitioned/sovai-accounting/processed/ratios_percentile_weekly.parq",
#             "name": "ratios_percentile_weekly_0.parquet",
#             "partitioned": False,
#         },
#         "market/prices": {
#             "url": "https://storage.googleapis.com/sovai-partitioned/sovai-accounting/prices.parq",
#             "name": "prices_0.parquet",
#             "partitioned": False,
#         },
#         "market/closeadj": {
#             "url": "https://storage.googleapis.com/sovai-partitioned/sovai-accounting/prices_closeadj.parq",
#             "name": "prices_closeadj_0.parquet",
#             "partitioned": False,
#         },
#         "complaints/public": {
#             "url": "https://storage.googleapis.com/sovai-partitioned/sovai-complaints/processed/consumer_complaint_public.parq",
#             "name": "consumer_complaint_0.parquet",
#             "partitioned": False,
#         },
#         "complaints/private": {
#             "url": "https://storage.googleapis.com/sovai-partitioned/sovai-complaints/processed/consumer_complaint_private.parq",
#             "name": "consumer_complaint_0.parquet",
#             "partitioned": False,
#         },
#         "lobbying/public": {
#             "url": "https://storage.googleapis.com/sovai-partitioned/sovai-lobbying/processed/lobbying_public.parq",
#             "name": "lobbying_public_0.parquet",
#             "partitioned": True,
#         },
#         "short/volume": {
#             "url": "https://storage.googleapis.com/sovai-partitioned/sovai-short/processed/short_volume_weekly.parq",
#             "name": "short_volume_weekly_0.parquet",
#             "partitioned": True,
#         },
#     }

#     if endpoint not in endpoint_config:
#         raise ValueError(f"Invalid endpoint: {endpoint}")

#     config = endpoint_config[endpoint]
#     base_url = config["url"]
#     name_file = config["name"]
#     partitioned = config["partitioned"]

#     # Load data
#     df_percentiles = load_data_for_tickers(
#         base_url, tickers, columns, start_date, end_date, name_file, partitioned
#     )
#     return CustomDataFrame(df_percentiles)
