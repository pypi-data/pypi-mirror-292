from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.delete_workspace_request_data import DeleteWorkspaceRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForWorkspaceApiHandlerType6")


@_attrs_define
class CrudApiRequestAndResponseDataForWorkspaceApiHandlerType6:
    """
    Attributes:
        delete_req (DeleteWorkspaceRequestData):
    """

    delete_req: "DeleteWorkspaceRequestData"

    def to_dict(self) -> Dict[str, Any]:
        delete_req = self.delete_req.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "DeleteReq": delete_req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.delete_workspace_request_data import DeleteWorkspaceRequestData

        d = src_dict.copy()
        delete_req = DeleteWorkspaceRequestData.from_dict(d.pop("DeleteReq"))

        crud_api_request_and_response_data_for_workspace_api_handler_type_6 = cls(
            delete_req=delete_req,
        )

        return crud_api_request_and_response_data_for_workspace_api_handler_type_6
