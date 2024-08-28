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
  from ..models.create_event_sink_args_type_1 import CreateEventSinkArgsType1
  from ..models.create_event_sink_args_type_0 import CreateEventSinkArgsType0
  from ..models.create_integration_args_type_0 import CreateIntegrationArgsType0
  from ..models.create_integration_args_type_1 import CreateIntegrationArgsType1





T = TypeVar("T", bound="CreateEventSinkRequestData")


@_attrs_define
class CreateEventSinkRequestData:
    """ 
        Attributes:
            description (str):
            name (str):
            tenant_id (str):
            event_sink_args (Union['CreateEventSinkArgsType0', 'CreateEventSinkArgsType1', None, Unset]):
            integration_args (Union['CreateIntegrationArgsType0', 'CreateIntegrationArgsType1', None, Unset]):
     """

    description: str
    name: str
    tenant_id: str
    event_sink_args: Union['CreateEventSinkArgsType0', 'CreateEventSinkArgsType1', None, Unset] = UNSET
    integration_args: Union['CreateIntegrationArgsType0', 'CreateIntegrationArgsType1', None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.create_event_sink_args_type_1 import CreateEventSinkArgsType1
        from ..models.create_event_sink_args_type_0 import CreateEventSinkArgsType0
        from ..models.create_integration_args_type_0 import CreateIntegrationArgsType0
        from ..models.create_integration_args_type_1 import CreateIntegrationArgsType1
        description = self.description

        name = self.name

        tenant_id = self.tenant_id

        event_sink_args: Union[Dict[str, Any], None, Unset]
        if isinstance(self.event_sink_args, Unset):
            event_sink_args = UNSET
        elif isinstance(self.event_sink_args, CreateEventSinkArgsType0):
            event_sink_args = self.event_sink_args.to_dict()
        elif isinstance(self.event_sink_args, CreateEventSinkArgsType1):
            event_sink_args = self.event_sink_args.to_dict()
        else:
            event_sink_args = self.event_sink_args

        integration_args: Union[Dict[str, Any], None, Unset]
        if isinstance(self.integration_args, Unset):
            integration_args = UNSET
        elif isinstance(self.integration_args, CreateIntegrationArgsType0):
            integration_args = self.integration_args.to_dict()
        elif isinstance(self.integration_args, CreateIntegrationArgsType1):
            integration_args = self.integration_args.to_dict()
        else:
            integration_args = self.integration_args


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "description": description,
            "name": name,
            "tenant_id": tenant_id,
        })
        if event_sink_args is not UNSET:
            field_dict["event_sink_args"] = event_sink_args
        if integration_args is not UNSET:
            field_dict["integration_args"] = integration_args

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_event_sink_args_type_1 import CreateEventSinkArgsType1
        from ..models.create_event_sink_args_type_0 import CreateEventSinkArgsType0
        from ..models.create_integration_args_type_0 import CreateIntegrationArgsType0
        from ..models.create_integration_args_type_1 import CreateIntegrationArgsType1
        d = src_dict.copy()
        description = d.pop("description")

        name = d.pop("name")

        tenant_id = d.pop("tenant_id")

        def _parse_event_sink_args(data: object) -> Union['CreateEventSinkArgsType0', 'CreateEventSinkArgsType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_event_sink_args_type_0 = CreateEventSinkArgsType0.from_dict(data)



                return componentsschemas_create_event_sink_args_type_0
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_event_sink_args_type_1 = CreateEventSinkArgsType1.from_dict(data)



                return componentsschemas_create_event_sink_args_type_1
            except: # noqa: E722
                pass
            return cast(Union['CreateEventSinkArgsType0', 'CreateEventSinkArgsType1', None, Unset], data)

        event_sink_args = _parse_event_sink_args(d.pop("event_sink_args", UNSET))


        def _parse_integration_args(data: object) -> Union['CreateIntegrationArgsType0', 'CreateIntegrationArgsType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_integration_args_type_0 = CreateIntegrationArgsType0.from_dict(data)



                return componentsschemas_create_integration_args_type_0
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_integration_args_type_1 = CreateIntegrationArgsType1.from_dict(data)



                return componentsschemas_create_integration_args_type_1
            except: # noqa: E722
                pass
            return cast(Union['CreateIntegrationArgsType0', 'CreateIntegrationArgsType1', None, Unset], data)

        integration_args = _parse_integration_args(d.pop("integration_args", UNSET))


        create_event_sink_request_data = cls(
            description=description,
            name=name,
            tenant_id=tenant_id,
            event_sink_args=event_sink_args,
            integration_args=integration_args,
        )


        create_event_sink_request_data.additional_properties = d
        return create_event_sink_request_data

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
