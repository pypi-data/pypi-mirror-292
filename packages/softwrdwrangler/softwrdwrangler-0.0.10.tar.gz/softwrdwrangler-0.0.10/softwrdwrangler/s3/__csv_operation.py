import boto3
import pandas as pd
import io
from .__utils import _parse_s3_uri


def read_csv(s3_uri: str) -> pd.DataFrame:
    """
    Reads a CSV file from S3 and returns it as a pandas DataFrame.

    :param s3_uri: S3 URI of the CSV file, e.g. 's3://bucket-name/path/to/file.csv'
    :return: Pandas DataFrame.
    """
    s3_client = boto3.client("s3")

    bucket_name, key = _parse_s3_uri(s3_uri)
    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return None

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        csv_data = response["Body"].read()
        df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
        return df
    except Exception as e:
        print(f"Error reading CSV file from S3: {e}")
        return None


def write_csv(df: pd.DataFrame, s3_uri: str) -> None:
    """
    Writes a pandas DataFrame to a CSV file in S3.

    :param df: Pandas DataFrame to write.
    :param s3_uri: S3 URI of the target CSV file, e.g. 's3://bucket-name/path/to/file.csv'
    """
    s3_client = boto3.client("s3")

    bucket_name, key = _parse_s3_uri(s3_uri)
    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return

    try:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=csv_buffer.getvalue())
        print(f"DataFrame successfully written to {s3_uri}")
    except Exception as e:
        print(f"Error writing CSV file to S3: {e}")
