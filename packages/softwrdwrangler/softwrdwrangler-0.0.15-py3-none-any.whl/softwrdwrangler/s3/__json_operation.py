import io
import json
from typing import Union
import boto3
import pandas as pd
from .__utils import _parse_s3_uri


def read_json(s3_uri: str) -> dict:
    """
    Reads a JSON file from S3 and returns it as a pandas DataFrame.

    :param s3_uri: S3 URI of the JSON file, e.g. 's3://bucket-name/path/to/file.json'
    :return: Pandas DataFrame.
    """
    s3_client = boto3.client("s3")

    bucket_name, key = _parse_s3_uri(s3_uri)
    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return None

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        json_data = response["Body"].read().decode("utf-8")
        data = json.loads(json_data)
        return data
    except Exception as e:
        print(f"Error reading JSON file from S3: {e}")
        return None

def to_json(file: Union[dict, list, pd.DataFrame, str], s3_uri: str) -> None:
    """
    Writes a dictionary, list, or pandas DataFrame to a JSON file in S3.

    :param file: Dictionary, list, or pandas DataFrame to write.
    :param s3_uri: S3 URI of the target JSON file, e.g. 's3://bucket-name/path/to/file.json'
    """
    s3_client = boto3.client("s3")

    bucket_name, key = _parse_s3_uri(s3_uri)
    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return

    # Check if the file is a DataFrame
    if isinstance(file, pd.DataFrame):
        try:
            json_data = file.to_dict(orient="records")
            json_str = json.dumps(json_data)

            s3_client.put_object(
                Bucket=bucket_name, Key=key, Body=json_str.encode("utf-8")
            )
            print(f"DataFrame successfully written to {s3_uri}")
        except Exception as e:
            print(f"Error writing JSON file to S3: {e}")

    # Check if the file is a dictionary
    elif isinstance(file, dict):
        try:
            json_str = json.dumps(file)
            s3_client.put_object(
                Bucket=bucket_name, Key=key, Body=json_str.encode("utf-8")
            )
            print(f"Dictionary successfully written to {s3_uri}")
        except Exception as e:
            print(f"Error writing JSON file to S3: {e}")
    # Check if the file is a list
    elif isinstance(file, list):
        try:
            json_str = json.dumps(file)
            s3_client.put_object(
                Bucket=bucket_name, Key=key, Body=json_str.encode("utf-8")
            )
            print(f"List successfully written to {s3_uri}")
        except Exception as e:
            print(f"Error writing JSON file to S3: {e}")
    # Check if the file is a string
    elif isinstance(file, str):
        try:
            s3_client.put_object(
                Bucket=bucket_name, Key=key, Body=file.encode("utf-8")
            )
            print(f"String successfully written to {s3_uri}")
        except Exception as e:
            print(f"Error writing JSON file to S3: {e}")

    else:
        print("Invalid file type. Please provide a DataFrame, dictionary, list, or string.")
        return
