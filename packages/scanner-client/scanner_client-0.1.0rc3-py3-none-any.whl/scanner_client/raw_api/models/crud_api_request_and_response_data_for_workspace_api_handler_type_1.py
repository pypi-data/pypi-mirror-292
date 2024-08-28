from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.list_workspaces_response_data import ListWorkspacesResponseData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForWorkspaceApiHandlerType1")


@_attrs_define
class CrudApiRequestAndResponseDataForWorkspaceApiHandlerType1:
    """
    Attributes:
        list_resp (ListWorkspacesResponseData):
    """

    list_resp: "ListWorkspacesResponseData"

    def to_dict(self) -> Dict[str, Any]:
        list_resp = self.list_resp.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "ListResp": list_resp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_workspaces_response_data import ListWorkspacesResponseData

        d = src_dict.copy()
        list_resp = ListWorkspacesResponseData.from_dict(d.pop("ListResp"))

        crud_api_request_and_response_data_for_workspace_api_handler_type_1 = cls(
            list_resp=list_resp,
        )

        return crud_api_request_and_response_data_for_workspace_api_handler_type_1
