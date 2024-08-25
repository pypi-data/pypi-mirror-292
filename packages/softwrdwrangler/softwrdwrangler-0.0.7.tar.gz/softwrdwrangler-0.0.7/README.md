# softwrdwrangler
It will wrangle various aws resources

## pre-requisites
you need to have aws cli installed and configured with the necessary permissions
[aws cli installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

```bash
aws configure
```

## Installation
```bash
pip install softwrdwrangler
```

## Usage
### S3 read and write pickle
```python
import softwrdwrangler as swr
data = swr.s3.read_pickle(<s3_uri>)
swr.s3.write_pickle(data, <s3_uri>)
```

### S3 read and write json
```python
import softwrdwrangler as swr
d = {'a': 1, 'b': 2}
swr.s3.write_json(d, 's3://bucket/key.json')
print(swr.s3.read_json('s3://bucket/key.json'))
```

### S3 read and write csv
```python
import softwrdwrangler as swr

data = swr.s3.read_csv(<s3_uri>)
swr.s3.write_csv(data, <s3_uri>)
```

## License
Apache Software License
```
