# Python client
API version: 0.1.1

## Requirements

- Python 3.10+
- Docker engine. [Documentation](https://docs.docker.com/engine/install/)

## Installation & Usage

1. If you don't have `Poetry` installed run:

```bash
pip install poetry
```

2. Install dependencies:

```bash
poetry config virtualenvs.in-project true
poetry install --no-root
```

3. Running tests:

```bash
poetry run pytest
```

You can test the application for multiple versions of Python. To do this, you need to install the required Python versions on your operating system, specify these versions in the tox.ini file, and then run the tests:
```bash
poetry run tox
```
Add the tox.ini file to `client/.openapi-generator-ignore` so that it doesn't get overwritten during client generation.

4. Building package:

```bash
poetry build
```

5. Publishing
```bash
poetry config pypi-token.pypi <pypi token>
poetry publish
```

## Client generator
To generate the client, execute the following script from the project root folder
```bash
poetry --directory server run python ./tools/client_generator/generate.py --file ./api/openapi.yaml
```

### Command
```bash
generate.py [--file <a path or URL to a .yaml file>] [--asyncio]
```

#### Arguments
**--file**
Specifies the input OpenAPI specification file path or URL. This argument is required for generating the Python client. The input file can be either a local file path or a URL pointing to the OpenAPI schema.

**--asyncio**
Flag to indicate whether to generate asynchronous code. If this flag is provided, the generated Python client will include asynchronous features. By default, synchronous code is generated.

#### Saving Arguments

The script saves provided arguments for future use. Upon the initial execution, if no arguments are provided, the script will check if there are previously saved arguments in the specified file path. If saved arguments are found, they will be loaded and used for generating the client. If no saved arguments are found or if new arguments are provided, the script will save the provided arguments for future use.

This mechanism ensures that users can omit specifying arguments on subsequent executions if the same arguments were used previously. Saved arguments are stored in a JSON file located at generator/args.json.

#### Configuration
You can change the name of the client package in the file `/tools/client_generator/config.json`.

Add file's paths to `client/.openapi-generator-ignore` so that it doesn't get overwritten during client generation.

#### Examples

```bash
python generate.py --file https://<domain>/openapi.json
python generate.py --file https://<domain>/openapi.json --asyncio
python generate.py --file /<path>/openapi.yaml
python generate.py --file /<path>/openapi.yaml --asyncio
python generate.py
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import ds_connector
from ds_connector.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = ds_connector.Configuration(
    host = "http://localhost"
)



# Enter a context with an instance of the API client
with ds_connector.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = ds_connector.DataProductApi(api_client)
    connector_id = 'connector_id_example' # str | 
    data_product_id = 'data_product_id_example' # str | 

    try:
        # Get a data product details
        api_response = api_instance.get_data_product(connector_id, data_product_id)
        print("The response of DataProductApi->get_data_product:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DataProductApi->get_data_product: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*DataProductApi* | [**get_data_product**](docs/DataProductApi.md#get_data_product) | **GET** /data-products/{connector_id}/{data_product_id}/ | Get a data product details
*DataProductApi* | [**get_data_products**](docs/DataProductApi.md#get_data_products) | **GET** /data-products/ | Get a list of data products
*DefaultApi* | [**health_check**](docs/DefaultApi.md#health_check) | **GET** /health-check/ | Health check
*DefaultApi* | [**metrics_metrics_get**](docs/DefaultApi.md#metrics_metrics_get) | **GET** /metrics | Metrics


## Documentation For Models

 - [Connector](docs/Connector.md)
 - [DataProduct](docs/DataProduct.md)
 - [HTTPValidationError](docs/HTTPValidationError.md)
 - [HealthCheck](docs/HealthCheck.md)
 - [Interface](docs/Interface.md)
 - [PaginatedResult](docs/PaginatedResult.md)
 - [Source](docs/Source.md)
 - [Tag](docs/Tag.md)
 - [ValidationError](docs/ValidationError.md)
 - [ValidationErrorLocInner](docs/ValidationErrorLocInner.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization

Endpoints do not require authorization.


## Author

all-hiro@hiro-microdatacenters.nl


