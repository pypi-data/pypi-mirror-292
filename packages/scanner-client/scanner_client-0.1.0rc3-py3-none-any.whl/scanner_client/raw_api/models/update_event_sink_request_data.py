from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast
from typing import Union
from ..types import UNSET, Unset
from typing import cast, Union

if TYPE_CHECKING:
  from ..models.update_event_sink_args_type_0 import UpdateEventSinkArgsType0
  from ..models.update_integration_args_type_1 import UpdateIntegrationArgsType1
  from ..models.update_event_sink_args_type_1 import UpdateEventSinkArgsType1
  from ..models.update_integration_args_type_0 import UpdateIntegrationArgsType0





T = TypeVar("T", bound="UpdateEventSinkRequestData")


@_attrs_define
class UpdateEventSinkRequestData:
    """ 
        Attributes:
            id (str):
            description (Union[Unset, str]): This implements a type which describes whether a value should be updated or
                not, that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
            event_sink_args (Union['UpdateEventSinkArgsType0', 'UpdateEventSinkArgsType1', Unset]):
            integration_args (Union['UpdateIntegrationArgsType0', 'UpdateIntegrationArgsType1', Unset]):
            name (Union[Unset, str]): This implements a type which describes whether a value should be updated or not,
                that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
     """

    id: str
    description: Union[Unset, str] = UNSET
    event_sink_args: Union['UpdateEventSinkArgsType0', 'UpdateEventSinkArgsType1', Unset] = UNSET
    integration_args: Union['UpdateIntegrationArgsType0', 'UpdateIntegrationArgsType1', Unset] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.update_event_sink_args_type_0 import UpdateEventSinkArgsType0
        from ..models.update_integration_args_type_1 import UpdateIntegrationArgsType1
        from ..models.update_event_sink_args_type_1 import UpdateEventSinkArgsType1
        from ..models.update_integration_args_type_0 import UpdateIntegrationArgsType0
        id = self.id

        description: Union[Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        event_sink_args: Union[Dict[str, Any], Unset]
        if isinstance(self.event_sink_args, Unset):
            event_sink_args = UNSET
        elif isinstance(self.event_sink_args, UpdateEventSinkArgsType0):
            event_sink_args = self.event_sink_args.to_dict()
        else:
            event_sink_args = self.event_sink_args.to_dict()


        integration_args: Union[Dict[str, Any], Unset]
        if isinstance(self.integration_args, Unset):
            integration_args = UNSET
        elif isinstance(self.integration_args, UpdateIntegrationArgsType0):
            integration_args = self.integration_args.to_dict()
        else:
            integration_args = self.integration_args.to_dict()


        name: Union[Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if event_sink_args is not UNSET:
            field_dict["event_sink_args"] = event_sink_args
        if integration_args is not UNSET:
            field_dict["integration_args"] = integration_args
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_event_sink_args_type_0 import UpdateEventSinkArgsType0
        from ..models.update_integration_args_type_1 import UpdateIntegrationArgsType1
        from ..models.update_event_sink_args_type_1 import UpdateEventSinkArgsType1
        from ..models.update_integration_args_type_0 import UpdateIntegrationArgsType0
        d = src_dict.copy()
        id = d.pop("id")

        def _parse_description(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_event_sink_args(data: object) -> Union['UpdateEventSinkArgsType0', 'UpdateEventSinkArgsType1', Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_update_event_sink_args_type_0 = UpdateEventSinkArgsType0.from_dict(data)



                return componentsschemas_update_event_sink_args_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_update_event_sink_args_type_1 = UpdateEventSinkArgsType1.from_dict(data)



            return componentsschemas_update_event_sink_args_type_1

        event_sink_args = _parse_event_sink_args(d.pop("event_sink_args", UNSET))


        def _parse_integration_args(data: object) -> Union['UpdateIntegrationArgsType0', 'UpdateIntegrationArgsType1', Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_update_integration_args_type_0 = UpdateIntegrationArgsType0.from_dict(data)



                return componentsschemas_update_integration_args_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_update_integration_args_type_1 = UpdateIntegrationArgsType1.from_dict(data)



            return componentsschemas_update_integration_args_type_1

        integration_args = _parse_integration_args(d.pop("integration_args", UNSET))


        def _parse_name(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))


        update_event_sink_request_data = cls(
            id=id,
            description=description,
            event_sink_args=event_sink_args,
            integration_args=integration_args,
            name=name,
        )


        update_event_sink_request_data.additional_properties = d
        return update_event_sink_request_data

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
