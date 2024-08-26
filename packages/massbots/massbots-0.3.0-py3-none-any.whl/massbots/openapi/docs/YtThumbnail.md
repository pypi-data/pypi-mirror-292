# YtThumbnail

YouTube thumbnail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** |  | [optional] 
**width** | **int** |  | [optional] 
**height** | **int** |  | [optional] 

## Example

```python
from openapi.models.yt_thumbnail import YtThumbnail

# TODO update the JSON string below
json = "{}"
# create an instance of YtThumbnail from a JSON string
yt_thumbnail_instance = YtThumbnail.from_json(json)
# print the JSON string representation of the object
print(YtThumbnail.to_json())

# convert the object into a dict
yt_thumbnail_dict = yt_thumbnail_instance.to_dict()
# create an instance of YtThumbnail from a dict
yt_thumbnail_from_dict = YtThumbnail.from_dict(yt_thumbnail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


