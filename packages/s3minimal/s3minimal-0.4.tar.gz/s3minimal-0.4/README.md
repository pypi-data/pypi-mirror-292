# s3minimal - The Minimalist S3 Library

![PyPI - Version](https://img.shields.io/pypi/v/s3minimal)


![PyPI - Python Version](https://img.shields.io/pypi/pyversions/s3minimal)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`s3minimal` is a Python library designed to simplify interactions with Amazon S3 using the `aiobotocore` and `botocore` libraries. It provides asynchronous and synchronous classes for various S3 operations.

## Installation

```bash
pip install s3minimal
```

## Usage

### Initialization

Initialize the `S3` class with your AWS credentials, endpoint URL, and region name.

```python
from s3minimal import S3

s3 = S3(
    endpoint_url="https://s3.amazonaws.com",
    region_name="us-east-1",
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
)

# or if you have environment variables set for your AWS credentials
s3 = S3()
```

For synchronous operations, you can use the `S3Sync` class in a similar manner, and all asynchronous methods described below can be called without `await`.

### Set Bucket

```python
s3.set_bucket("your_bucket_name")
```

### Download File

```python
file = await s3.download("path/to/your/file")
```

### Upload File

```python
with open("path/to/your/local/file", "rb") as f:
    file_obj = io.BytesIO(f.read())

await s3.upload("path/to/your/s3/file", file_obj)
```

### Move File

```python
await s3.move("path/to/source/file", "path/to/destination/file")
```

### Generate Presigned URL

```python
url = await s3.generate_presigned_url("path/to/your/file")
```

### Create Bucket

Create a new S3 bucket:

```python
await s3.create_bucket("new_bucket_name")
```

To set CORS configurations during bucket creation, pass the `set_cors` parameter as `True` and provide the `cors_configuration`:

```python
cors_configuration = {
    "CORSRules": [
        {
            "AllowedHeaders": ["Access-Control-Allow-Origin", "*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
            "AllowedOrigins": ["*"],
            "MaxAgeSeconds": 60,
        }
    ]
}

await s3.create_bucket("new_bucket_name", set_cors=True, cors_configuration=cors_configuration)
```

### List Files

```python
files = await s3.list_files("path/in/your/bucket")
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
