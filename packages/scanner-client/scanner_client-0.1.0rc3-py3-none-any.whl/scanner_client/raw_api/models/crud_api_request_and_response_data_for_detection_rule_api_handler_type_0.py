from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.list_detection_rules_request_data import ListDetectionRulesRequestData





T = TypeVar("T", bound="CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType0")


@_attrs_define
class CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType0:
    """ 
        Attributes:
            list_req (ListDetectionRulesRequestData):
     """

    list_req: 'ListDetectionRulesRequestData'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.list_detection_rules_request_data import ListDetectionRulesRequestData
        list_req = self.list_req.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "ListReq": list_req,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_detection_rules_request_data import ListDetectionRulesRequestData
        d = src_dict.copy()
        list_req = ListDetectionRulesRequestData.from_dict(d.pop("ListReq"))




        crud_api_request_and_response_data_for_detection_rule_api_handler_type_0 = cls(
            list_req=list_req,
        )

        return crud_api_request_and_response_data_for_detection_rule_api_handler_type_0

