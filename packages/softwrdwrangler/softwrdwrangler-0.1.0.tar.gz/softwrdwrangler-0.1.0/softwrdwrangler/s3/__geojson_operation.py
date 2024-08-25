from typing import Union
import boto3
import json
import geojson
from .__utils import _parse_s3_uri


def read_geojson(s3_uri: str) -> dict:
    """
    Reads a GeoJSON file from S3 and returns it as a dictionary.

    :param s3_uri: S3 URI of the GeoJSON file, e.g. 's3://bucket-name/path/to/file.geojson'
    :return: Dictionary representation of the GeoJSON data; None if invalid or read error occurs.
    """
    s3_client = boto3.client("s3")

    bucket_name, key = _parse_s3_uri(s3_uri)
    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return None

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        geojson_data = response["Body"].read().decode('utf-8')
        geojson_dict = json.loads(geojson_data)
        is_valid, error_msg = _is_valid_geojson(geojson_dict)
        if not is_valid:
            print(f"Invalid GeoJSON data: {error_msg}")
            return None
        return geojson_dict
    except Exception as e:
        print(f"Error reading GeoJSON file from S3: {e}")
        return None


def write_geojson(geojson_dict: dict, s3_uri: str) -> None:
    """
    Writes a dictionary as a GeoJSON file to S3.

    :param geojson_dict: Dictionary representation of the GeoJSON data.
    :param s3_uri: S3 URI of the target GeoJSON file, e.g. 's3://bucket-name/path/to/file.geojson'
    """
    s3_client = boto3.client("s3")

    bucket_name, key = _parse_s3_uri(s3_uri)
    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return

    is_valid, error_msg = _is_valid_geojson(geojson_dict)
    if not is_valid:
        print(f"Invalid GeoJSON data: {error_msg}")
        return

    try:
        geojson_data = json.dumps(geojson_dict)
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=geojson_data)
        print(f"GeoJSON file successfully written to {s3_uri}")
    except Exception as e:
        print(f"Error writing GeoJSON file to S3: {e}")


def _is_valid_geojson(geojson_dict: dict) -> Union[bool, str]:
    """
    Checks if the provided dictionary is a valid GeoJSON object.

    :param geojson_dict: Dictionary representing the GeoJSON data.
    :return: Tuple containing (is_valid: bool, error_msg: str).
    """
    try:
        # Attempt to create a GeoJSON object and validate it
        geojson_object = geojson.loads(json.dumps(geojson_dict))
        result = geojson.is_valid(geojson_object)
        if result['valid']:
            return True, ""
        else:
            return False, result['message']
    except Exception as e:
        return False, str(e)
