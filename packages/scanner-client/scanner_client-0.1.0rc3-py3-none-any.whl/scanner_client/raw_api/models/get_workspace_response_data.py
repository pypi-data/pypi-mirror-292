from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.workspace import Workspace


T = TypeVar("T", bound="GetWorkspaceResponseData")


@_attrs_define
class GetWorkspaceResponseData:
    """
    Attributes:
        workspace (Workspace):
    """

    workspace: "Workspace"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        workspace = self.workspace.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace": workspace,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.workspace import Workspace

        d = src_dict.copy()
        workspace = Workspace.from_dict(d.pop("workspace"))

        get_workspace_response_data = cls(
            workspace=workspace,
        )

        get_workspace_response_data.additional_properties = d
        return get_workspace_response_data

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
