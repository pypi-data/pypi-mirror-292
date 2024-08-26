# ApiBalance

Token balance in points.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**balance** | **int** |  | [optional] 

## Example

```python
from openapi.models.api_balance import ApiBalance

# TODO update the JSON string below
json = "{}"
# create an instance of ApiBalance from a JSON string
api_balance_instance = ApiBalance.from_json(json)
# print the JSON string representation of the object
print(ApiBalance.to_json())

# convert the object into a dict
api_balance_dict = api_balance_instance.to_dict()
# create an instance of ApiBalance from a dict
api_balance_from_dict = ApiBalance.from_dict(api_balance_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


