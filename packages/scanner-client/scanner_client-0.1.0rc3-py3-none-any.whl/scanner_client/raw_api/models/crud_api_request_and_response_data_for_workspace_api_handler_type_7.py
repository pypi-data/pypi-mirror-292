from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.delete_workspace_response_data import DeleteWorkspaceResponseData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForWorkspaceApiHandlerType7")


@_attrs_define
class CrudApiRequestAndResponseDataForWorkspaceApiHandlerType7:
    """
    Attributes:
        delete_resp (DeleteWorkspaceResponseData):
    """

    delete_resp: "DeleteWorkspaceResponseData"

    def to_dict(self) -> Dict[str, Any]:
        delete_resp = self.delete_resp.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "DeleteResp": delete_resp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.delete_workspace_response_data import DeleteWorkspaceResponseData

        d = src_dict.copy()
        delete_resp = DeleteWorkspaceResponseData.from_dict(d.pop("DeleteResp"))

        crud_api_request_and_response_data_for_workspace_api_handler_type_7 = cls(
            delete_resp=delete_resp,
        )

        return crud_api_request_and_response_data_for_workspace_api_handler_type_7
