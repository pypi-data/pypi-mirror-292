# openapi.ApiGroup

All URIs are relative to *https://api.massbots.xyz*

Method | HTTP request | Description
------------- | ------------- | -------------
[**balance_get**](ApiGroup.md#balance_get) | **GET** /balance | Get balance


# **balance_get**
> ApiBalance balance_get()

Get balance

Returns users balance.

### Example

* Api Key Authentication (Token):

```python
import openapi
from openapi.models.api_balance import ApiBalance
from openapi.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.massbots.xyz
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi.Configuration(
    host = "https://api.massbots.xyz"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: Token
configuration.api_key['Token'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Token'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi.ApiGroup(api_client)

    try:
        # Get balance
        api_response = api_instance.balance_get()
        print("The response of ApiGroup->balance_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApiGroup->balance_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ApiBalance**](ApiBalance.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**500** | Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

