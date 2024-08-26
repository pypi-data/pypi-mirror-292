# DlVideo

Video with available formats

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**formats** | [**Dict[str, DlVideoFormat]**](DlVideoFormat.md) | Available formats | [optional] 

## Example

```python
from openapi.models.dl_video import DlVideo

# TODO update the JSON string below
json = "{}"
# create an instance of DlVideo from a JSON string
dl_video_instance = DlVideo.from_json(json)
# print the JSON string representation of the object
print(DlVideo.to_json())

# convert the object into a dict
dl_video_dict = dl_video_instance.to_dict()
# create an instance of DlVideo from a dict
dl_video_from_dict = DlVideo.from_dict(dl_video_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


