# YtChannel

YouTube channel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**url** | **str** |  | [optional] 
**banner_url** | **str** |  | [optional] 
**comment_count** | **int** |  | [optional] 
**subscriber_count** | **int** |  | [optional] 
**video_count** | **int** |  | [optional] 
**view_count** | **int** |  | [optional] 
**thumbnails** | [**Dict[str, YtThumbnail]**](YtThumbnail.md) |  | [optional] 

## Example

```python
from openapi.models.yt_channel import YtChannel

# TODO update the JSON string below
json = "{}"
# create an instance of YtChannel from a JSON string
yt_channel_instance = YtChannel.from_json(json)
# print the JSON string representation of the object
print(YtChannel.to_json())

# convert the object into a dict
yt_channel_dict = yt_channel_instance.to_dict()
# create an instance of YtChannel from a dict
yt_channel_from_dict = YtChannel.from_dict(yt_channel_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


