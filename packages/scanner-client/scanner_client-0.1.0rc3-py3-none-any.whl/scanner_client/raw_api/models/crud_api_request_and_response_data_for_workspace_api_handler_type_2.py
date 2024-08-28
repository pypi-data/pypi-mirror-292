from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.create_workspace_request_data import CreateWorkspaceRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForWorkspaceApiHandlerType2")


@_attrs_define
class CrudApiRequestAndResponseDataForWorkspaceApiHandlerType2:
    """
    Attributes:
        create_req (CreateWorkspaceRequestData):
    """

    create_req: "CreateWorkspaceRequestData"

    def to_dict(self) -> Dict[str, Any]:
        create_req = self.create_req.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "CreateReq": create_req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_workspace_request_data import CreateWorkspaceRequestData

        d = src_dict.copy()
        create_req = CreateWorkspaceRequestData.from_dict(d.pop("CreateReq"))

        crud_api_request_and_response_data_for_workspace_api_handler_type_2 = cls(
            create_req=create_req,
        )

        return crud_api_request_and_response_data_for_workspace_api_handler_type_2
