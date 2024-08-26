# openapi.YoutubeGroup

All URIs are relative to *https://api.massbots.xyz*

Method | HTTP request | Description
------------- | ------------- | -------------
[**yt_channel_id_get**](YoutubeGroup.md#yt_channel_id_get) | **GET** /yt/channel/{id} | Get channel
[**yt_search_get**](YoutubeGroup.md#yt_search_get) | **GET** /yt/search | Search videos
[**yt_video_id_get**](YoutubeGroup.md#yt_video_id_get) | **GET** /yt/video/{id} | Get video


# **yt_channel_id_get**
> YtChannel yt_channel_id_get(id)

Get channel

Retrieves details of a YouTube channel by its ID.

### Example

* Api Key Authentication (Token):

```python
import openapi
from openapi.models.yt_channel import YtChannel
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
    api_instance = openapi.YoutubeGroup(api_client)
    id = 'id_example' # str | Channel ID

    try:
        # Get channel
        api_response = api_instance.yt_channel_id_get(id)
        print("The response of YoutubeGroup->yt_channel_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling YoutubeGroup->yt_channel_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Channel ID | 

### Return type

[**YtChannel**](YtChannel.md)

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

# **yt_search_get**
> List[YtVideo] yt_search_get(q)

Search videos

YouTube search for videos by a query.

### Example

* Api Key Authentication (Token):

```python
import openapi
from openapi.models.yt_video import YtVideo
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
    api_instance = openapi.YoutubeGroup(api_client)
    q = 'q_example' # str | Query

    try:
        # Search videos
        api_response = api_instance.yt_search_get(q)
        print("The response of YoutubeGroup->yt_search_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling YoutubeGroup->yt_search_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**| Query | 

### Return type

[**List[YtVideo]**](YtVideo.md)

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

# **yt_video_id_get**
> YtVideo yt_video_id_get(id)

Get video

Retrieves details of a YouTube video by its ID.

### Example

* Api Key Authentication (Token):

```python
import openapi
from openapi.models.yt_video import YtVideo
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
    api_instance = openapi.YoutubeGroup(api_client)
    id = 'id_example' # str | Video ID

    try:
        # Get video
        api_response = api_instance.yt_video_id_get(id)
        print("The response of YoutubeGroup->yt_video_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling YoutubeGroup->yt_video_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Video ID | 

### Return type

[**YtVideo**](YtVideo.md)

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

