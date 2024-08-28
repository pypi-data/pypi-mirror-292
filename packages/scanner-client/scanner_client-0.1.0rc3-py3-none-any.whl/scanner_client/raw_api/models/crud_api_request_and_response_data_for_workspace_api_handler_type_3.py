from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_workspace_request_data import GetWorkspaceRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForWorkspaceApiHandlerType3")


@_attrs_define
class CrudApiRequestAndResponseDataForWorkspaceApiHandlerType3:
    """
    Attributes:
        read_req (GetWorkspaceRequestData):
    """

    read_req: "GetWorkspaceRequestData"

    def to_dict(self) -> Dict[str, Any]:
        read_req = self.read_req.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "ReadReq": read_req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_workspace_request_data import GetWorkspaceRequestData

        d = src_dict.copy()
        read_req = GetWorkspaceRequestData.from_dict(d.pop("ReadReq"))

        crud_api_request_and_response_data_for_workspace_api_handler_type_3 = cls(
            read_req=read_req,
        )

        return crud_api_request_and_response_data_for_workspace_api_handler_type_3
