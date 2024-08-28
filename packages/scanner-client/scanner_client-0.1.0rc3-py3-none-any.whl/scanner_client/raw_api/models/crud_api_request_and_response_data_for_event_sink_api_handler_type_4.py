from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.get_event_sink_response_data import GetEventSinkResponseData





T = TypeVar("T", bound="CrudApiRequestAndResponseDataForEventSinkApiHandlerType4")


@_attrs_define
class CrudApiRequestAndResponseDataForEventSinkApiHandlerType4:
    """ 
        Attributes:
            read_resp (GetEventSinkResponseData):
     """

    read_resp: 'GetEventSinkResponseData'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.get_event_sink_response_data import GetEventSinkResponseData
        read_resp = self.read_resp.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "ReadResp": read_resp,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_event_sink_response_data import GetEventSinkResponseData
        d = src_dict.copy()
        read_resp = GetEventSinkResponseData.from_dict(d.pop("ReadResp"))




        crud_api_request_and_response_data_for_event_sink_api_handler_type_4 = cls(
            read_resp=read_resp,
        )

        return crud_api_request_and_response_data_for_event_sink_api_handler_type_4

