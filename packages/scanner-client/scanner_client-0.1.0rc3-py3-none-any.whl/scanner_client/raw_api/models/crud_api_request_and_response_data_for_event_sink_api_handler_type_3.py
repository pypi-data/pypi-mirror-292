from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.get_event_sink_request_data import GetEventSinkRequestData





T = TypeVar("T", bound="CrudApiRequestAndResponseDataForEventSinkApiHandlerType3")


@_attrs_define
class CrudApiRequestAndResponseDataForEventSinkApiHandlerType3:
    """ 
        Attributes:
            read_req (GetEventSinkRequestData):
     """

    read_req: 'GetEventSinkRequestData'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.get_event_sink_request_data import GetEventSinkRequestData
        read_req = self.read_req.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "ReadReq": read_req,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_event_sink_request_data import GetEventSinkRequestData
        d = src_dict.copy()
        read_req = GetEventSinkRequestData.from_dict(d.pop("ReadReq"))




        crud_api_request_and_response_data_for_event_sink_api_handler_type_3 = cls(
            read_req=read_req,
        )

        return crud_api_request_and_response_data_for_event_sink_api_handler_type_3

