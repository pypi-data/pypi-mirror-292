[![Publish Python Package](https://github.com/softwrdai/softwrdwrangler/actions/workflows/publish_2_pypi.yml/badge.svg)](https://github.com/softwrdai/softwrdwrangler/actions/workflows/publish_2_pypi.yml)

# softwrdwrangler

`softwrdwrangler` is a Python package designed to simplify and streamline operations on various AWS resources, primarily focusing on S3. It offers utilities for reading and writing different file formats and managing S3 objects efficiently.

## Pre-requisites

You need to have AWS CLI installed and configured with the necessary permissions to interact with AWS services.

### Install AWS CLI
Follow the installation guide here: [AWS CLI Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

Once installed, configure it by running:
```bash
aws configure
```

## Installation

Install the package via pip:
```bash
pip install softwrdwrangler
```

## Usage

### S3 Operations

#### S3 Read and Write Pickle
```python
import softwrdwrangler as swr

# Reading a pickle file from S3
data = swr.read_pickle('s3://bucket-name/path/to/file.pkl')

# Writing a DataFrame to a pickle file in S3
swr.write_pickle(data, 's3://bucket-name/path/to/file.pkl')
```

#### S3 Read and Write JSON
```python
import softwrdwrangler as swr

# Writing a dictionary to a JSON file in S3
data = {'a': 1, 'b': 2}
swr.write_json(data, 's3://bucket-name/path/to/file.json')

# Reading a JSON file from S3
print(swr.read_json('s3://bucket-name/path/to/file.json'))
```

#### S3 Read and Write CSV
```python
import softwrdwrangler as swr

# Reading a CSV file from S3
data = swr.read_csv('s3://bucket-name/path/to/file.csv')

# Writing a DataFrame to a CSV file in S3
swr.write_csv(data, 's3://bucket-name/path/to/file.csv')
```

#### S3 Read and Write GeoJSON
```python
import softwrdwrangler as swr

# Reading a GeoJSON file from S3
data = swr.read_geojson('s3://bucket-name/path/to/file.geojson')

# Writing a dictionary to a GeoJSON file in S3
swr.write_geojson(data, 's3://bucket-name/path/to/file.geojson')
```

### Additional S3 Utilities

#### List Files
List all files in a specified S3 bucket and prefix.
```python
import softwrdwrangler as swr

files = swr.list_files('s3://bucket-name/path/to/folder/')
print(files)
```

#### Delete File
Delete a specific file from S3.
```python
import softwrdwrangler as swr

swr.delete_file('s3://bucket-name/path/to/file')
```

#### Upload Local File to S3
Upload a file from local storage to S3.
```python
import softwrdwrangler as swr

swr.upload_file('/local/path/to/file', 's3://bucket-name/path/to/file')
```

#### Download S3 File to Local Storage
Download a file from S3 to local storage.
```python
import softwrdwrangler as swr

swr.download_file('s3://bucket-name/path/to/file', '/local/path/to/file')
```

#### Copy File within S3
Copy a file from one S3 location to another.
```python
import softwrdwrangler as swr

swr.copy_file('s3://source-bucket/path/to/file', 's3://destination-bucket/path/to/file')
```

#### Generate Pre-signed URL
Generate a pre-signed URL to grant temporary access to an S3 object.
```python
import softwrdwrangler as swr

url = swr.generate_presigned_url('s3://bucket-name/path/to/file', expiration=3600)
print(url)
```

### Advanced Operations

#### Get Latest Date-stamped Folder (ds_nodash)
Retrieve the latest date-stamped folder (e.g., `20221201`) from a given S3 prefix, with an optional skip count.
```python
import softwrdwrangler as swr

latest_date = swr.get_latest_ds_nodash('s3://bucket-name/path', skip=1)
if latest_date:
    print(f"Latest ds_nodash after skipping 1: {latest_date}")
else:
    print("No valid date folders found or error occurred.")
```

## License

`softwrdwrangler` is licensed under the Apache Software License.

```
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
```

---
