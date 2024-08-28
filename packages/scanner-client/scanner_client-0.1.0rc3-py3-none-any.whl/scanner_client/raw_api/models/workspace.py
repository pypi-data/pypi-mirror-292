import datetime
from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="Workspace")


@_attrs_define
class Workspace:
    """
    Attributes:
        created_at (datetime.datetime):
        description (str):
        id (str):
        name (str):
        tenant_id (str):
        updated_at (datetime.datetime):
    """

    created_at: datetime.datetime
    description: str
    id: str
    name: str
    tenant_id: str
    updated_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()

        description = self.description

        id = self.id

        name = self.name

        tenant_id = self.tenant_id

        updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "description": description,
                "id": id,
                "name": name,
                "tenant_id": tenant_id,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        description = d.pop("description")

        id = d.pop("id")

        name = d.pop("name")

        tenant_id = d.pop("tenant_id")

        updated_at = isoparse(d.pop("updated_at"))

        workspace = cls(
            created_at=created_at,
            description=description,
            id=id,
            name=name,
            tenant_id=tenant_id,
            updated_at=updated_at,
        )

        workspace.additional_properties = d
        return workspace

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
