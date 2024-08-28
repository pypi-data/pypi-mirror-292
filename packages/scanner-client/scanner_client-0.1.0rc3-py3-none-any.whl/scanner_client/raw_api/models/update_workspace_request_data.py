from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateWorkspaceRequestData")


@_attrs_define
class UpdateWorkspaceRequestData:
    """
    Attributes:
        id (str):
        description (Union[Unset, str]): This implements a type which describes whether a value should be updated or
            not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        name (Union[Unset, str]): This implements a type which describes whether a value should be updated or not,
            that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
    """

    id: str
    description: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        description: Union[Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        name: Union[Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        def _parse_description(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_name(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        update_workspace_request_data = cls(
            id=id,
            description=description,
            name=name,
        )

        update_workspace_request_data.additional_properties = d
        return update_workspace_request_data

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
