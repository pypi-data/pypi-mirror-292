# openapi.DownloadGroup

All URIs are relative to *https://api.massbots.xyz*

Method | HTTP request | Description
------------- | ------------- | -------------
[**dl_video_id_cached_f_get**](DownloadGroup.md#dl_video_id_cached_f_get) | **GET** /dl/video/{id}/cached/{f} | Get cached video
[**dl_video_id_download_f_get**](DownloadGroup.md#dl_video_id_download_f_get) | **GET** /dl/video/{id}/download/{f} | Download video
[**dl_video_id_get**](DownloadGroup.md#dl_video_id_get) | **GET** /dl/video/{id} | Get video formats


# **dl_video_id_cached_f_get**
> DlFileID dl_video_id_cached_f_get(id, f)

Get cached video

Instantly returns previously downloaded video. 

### Example

* Api Key Authentication (Token):

```python
import openapi
from openapi.models.dl_file_id import DlFileID
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
    api_instance = openapi.DownloadGroup(api_client)
    id = 'id_example' # str | Video ID
    f = 'f_example' # str | Format (e.g. 360p, 720p)

    try:
        # Get cached video
        api_response = api_instance.dl_video_id_cached_f_get(id, f)
        print("The response of DownloadGroup->dl_video_id_cached_f_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DownloadGroup->dl_video_id_cached_f_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Video ID | 
 **f** | **str**| Format (e.g. 360p, 720p) | 

### Return type

[**DlFileID**](DlFileID.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Not Found |  -  |
**500** | Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dl_video_id_download_f_get**
> DlResult dl_video_id_download_f_get(id, f)

Download video

Initiates video downloading in the specified format. Use the same method to get the status of downloading. Once the downloading is ready, `file_id` will be included in the response.

### Example

* Api Key Authentication (Token):

```python
import openapi
from openapi.models.dl_result import DlResult
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
    api_instance = openapi.DownloadGroup(api_client)
    id = 'id_example' # str | Video ID
    f = 'f_example' # str | Format (e.g. 360p, 720p)

    try:
        # Download video
        api_response = api_instance.dl_video_id_download_f_get(id, f)
        print("The response of DownloadGroup->dl_video_id_download_f_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DownloadGroup->dl_video_id_download_f_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Video ID | 
 **f** | **str**| Format (e.g. 360p, 720p) | 

### Return type

[**DlResult**](DlResult.md)

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

# **dl_video_id_get**
> DlVideo dl_video_id_get(id)

Get video formats

Returns available video formats for downloading. Formats that are already cached are marked as such.<br> - Use <ins>[Get cached video](#tag/download/GET/dl/video/{id}/cached/{f})</ins> to get the file ID instantly.<br> - Use <ins>[Download video](#tag/download/GET/dl/video/{id}/download/{f})</ins> to start a new downloading. 

### Example

* Api Key Authentication (Token):

```python
import openapi
from openapi.models.dl_video import DlVideo
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
    api_instance = openapi.DownloadGroup(api_client)
    id = 'id_example' # str | Video ID

    try:
        # Get video formats
        api_response = api_instance.dl_video_id_get(id)
        print("The response of DownloadGroup->dl_video_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DownloadGroup->dl_video_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Video ID | 

### Return type

[**DlVideo**](DlVideo.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Not Found |  -  |
**500** | Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

