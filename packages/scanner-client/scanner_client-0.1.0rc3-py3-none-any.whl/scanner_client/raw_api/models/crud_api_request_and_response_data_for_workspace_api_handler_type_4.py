from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_workspace_response_data import GetWorkspaceResponseData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForWorkspaceApiHandlerType4")


@_attrs_define
class CrudApiRequestAndResponseDataForWorkspaceApiHandlerType4:
    """
    Attributes:
        read_resp (GetWorkspaceResponseData):
    """

    read_resp: "GetWorkspaceResponseData"

    def to_dict(self) -> Dict[str, Any]:
        read_resp = self.read_resp.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "ReadResp": read_resp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_workspace_response_data import GetWorkspaceResponseData

        d = src_dict.copy()
        read_resp = GetWorkspaceResponseData.from_dict(d.pop("ReadResp"))

        crud_api_request_and_response_data_for_workspace_api_handler_type_4 = cls(
            read_resp=read_resp,
        )

        return crud_api_request_and_response_data_for_workspace_api_handler_type_4
