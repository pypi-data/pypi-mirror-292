# DlVideoFormat

Video format

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | **str** | Video resolution | [optional] 
**cached** | **bool** | Set to &#x60;true&#x60; if the format is cached for quick downloading&lt;br&gt; See: &lt;ins&gt;[Get cached video](#tag/download/GET/dl/video/{id}/cached/{f})&lt;/ins&gt;  | [optional] 
**file_size** | **int** | File size in bytes, available only if video is not cached  | [optional] 

## Example

```python
from openapi.models.dl_video_format import DlVideoFormat

# TODO update the JSON string below
json = "{}"
# create an instance of DlVideoFormat from a JSON string
dl_video_format_instance = DlVideoFormat.from_json(json)
# print the JSON string representation of the object
print(DlVideoFormat.to_json())

# convert the object into a dict
dl_video_format_dict = dl_video_format_instance.to_dict()
# create an instance of DlVideoFormat from a dict
dl_video_format_from_dict = DlVideoFormat.from_dict(dl_video_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


