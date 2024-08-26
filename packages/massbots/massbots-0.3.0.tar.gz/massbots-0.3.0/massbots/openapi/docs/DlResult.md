# DlResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | One of: &#x60;queued&#x60;, &#x60;downloading&#x60;, &#x60;ready&#x60;, &#x60;failed&#x60;  | [optional] 
**file_id** | **str** | Telegram&#39;s &#x60;file_id&#x60; used for sending cached files  | [optional] 

## Example

```python
from openapi.models.dl_result import DlResult

# TODO update the JSON string below
json = "{}"
# create an instance of DlResult from a JSON string
dl_result_instance = DlResult.from_json(json)
# print the JSON string representation of the object
print(DlResult.to_json())

# convert the object into a dict
dl_result_dict = dl_result_instance.to_dict()
# create an instance of DlResult from a dict
dl_result_from_dict = DlResult.from_dict(dl_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


