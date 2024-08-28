from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.get_detection_rule_request_data import GetDetectionRuleRequestData





T = TypeVar("T", bound="CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType3")


@_attrs_define
class CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType3:
    """ 
        Attributes:
            read_req (GetDetectionRuleRequestData):
     """

    read_req: 'GetDetectionRuleRequestData'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.get_detection_rule_request_data import GetDetectionRuleRequestData
        read_req = self.read_req.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "ReadReq": read_req,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_detection_rule_request_data import GetDetectionRuleRequestData
        d = src_dict.copy()
        read_req = GetDetectionRuleRequestData.from_dict(d.pop("ReadReq"))




        crud_api_request_and_response_data_for_detection_rule_api_handler_type_3 = cls(
            read_req=read_req,
        )

        return crud_api_request_and_response_data_for_detection_rule_api_handler_type_3

