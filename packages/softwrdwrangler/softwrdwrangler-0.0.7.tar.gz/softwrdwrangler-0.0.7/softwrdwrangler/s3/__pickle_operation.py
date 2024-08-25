import boto3
import pandas as pd
import io
from .__utils import _parse_s3_uri


def read_pickle(s3_uri: str) -> pd.DataFrame:
    """
    Reads a pickle file from S3 and returns it as a pandas DataFrame.
    :param s3_uri: S3 URI of the pickle file, e.g. 's3://bucket-name/path/to/file.pkl'
    :return: Pandas DataFrame.
    """
    s3_client = boto3.client("s3")

    bucket_name, key = _parse_s3_uri(s3_uri)
    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return None

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        pickle_data = response["Body"].read()
        df = pd.read_pickle(io.BytesIO(pickle_data))
        return df
    except Exception as e:
        print(f"Error reading pickle file from S3: {e}")
        return None


def write_pickle(df: pd.DataFrame, s3_uri: str) -> None:
    """
    Writes a pandas DataFrame to a pickle file in S3.

    :param df: Pandas DataFrame to write.
    :param s3_uri: S3 URI of the target pickle file, e.g. 's3://bucket-name/path/to/file.pkl'
    """
    s3_client = boto3.client("s3")

    bucket_name, key = _parse_s3_uri(s3_uri)
    if not bucket_name or not key:
        print("Invalid S3 URI.")
        return

    try:
        pickle_buffer = io.BytesIO()
        df.to_pickle(pickle_buffer)
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=pickle_buffer.getvalue())
        print(f"DataFrame successfully written to {s3_uri}")
    except Exception as e:
        print(f"Error writing pickle file to S3: {e}")
