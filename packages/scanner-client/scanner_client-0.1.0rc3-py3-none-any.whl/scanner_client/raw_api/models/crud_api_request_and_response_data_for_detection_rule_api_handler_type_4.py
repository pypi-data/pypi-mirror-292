from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.get_detection_rule_response_data import GetDetectionRuleResponseData





T = TypeVar("T", bound="CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType4")


@_attrs_define
class CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType4:
    """ 
        Attributes:
            read_resp (GetDetectionRuleResponseData):
     """

    read_resp: 'GetDetectionRuleResponseData'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.get_detection_rule_response_data import GetDetectionRuleResponseData
        read_resp = self.read_resp.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "ReadResp": read_resp,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_detection_rule_response_data import GetDetectionRuleResponseData
        d = src_dict.copy()
        read_resp = GetDetectionRuleResponseData.from_dict(d.pop("ReadResp"))




        crud_api_request_and_response_data_for_detection_rule_api_handler_type_4 = cls(
            read_resp=read_resp,
        )

        return crud_api_request_and_response_data_for_detection_rule_api_handler_type_4

