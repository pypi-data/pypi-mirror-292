import re
def _parse_s3_uri(s3_uri):
    """
    Parses an S3 URI into bucket name and key.

    :param s3_uri: S3 URI of the pickle file, e.g. 's3://bucket-name/path/to/file.pkl'
    :return: tuple of (bucket_name, key).
    """
    match = re.match(r"s3://([^/]+)/(.+)", s3_uri)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None
