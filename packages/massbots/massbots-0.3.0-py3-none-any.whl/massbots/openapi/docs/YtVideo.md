# YtVideo

YouTube video

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**url** | **str** |  | [optional] 
**published_at** | **str** |  | [optional] 
**category_id** | **str** |  | [optional] 
**channel_id** | **str** |  | [optional] 
**channel_title** | **str** |  | [optional] 
**channel_url** | **str** |  | [optional] 
**comment_count** | **int** |  | [optional] 
**like_count** | **int** |  | [optional] 
**view_count** | **int** |  | [optional] 
**thumbnails** | [**Dict[str, YtThumbnail]**](YtThumbnail.md) |  | [optional] 

## Example

```python
from openapi.models.yt_video import YtVideo

# TODO update the JSON string below
json = "{}"
# create an instance of YtVideo from a JSON string
yt_video_instance = YtVideo.from_json(json)
# print the JSON string representation of the object
print(YtVideo.to_json())

# convert the object into a dict
yt_video_dict = yt_video_instance.to_dict()
# create an instance of YtVideo from a dict
yt_video_from_dict = YtVideo.from_dict(yt_video_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


