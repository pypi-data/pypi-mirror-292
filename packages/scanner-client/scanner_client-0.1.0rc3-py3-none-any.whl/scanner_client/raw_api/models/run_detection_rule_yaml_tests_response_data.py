from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.run_detection_rule_yaml_tests_response_data_results import RunDetectionRuleYamlTestsResponseDataResults





T = TypeVar("T", bound="RunDetectionRuleYamlTestsResponseData")


@_attrs_define
class RunDetectionRuleYamlTestsResponseData:
    """ 
        Attributes:
            results (RunDetectionRuleYamlTestsResponseDataResults):
     """

    results: 'RunDetectionRuleYamlTestsResponseDataResults'
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.run_detection_rule_yaml_tests_response_data_results import RunDetectionRuleYamlTestsResponseDataResults
        results = self.results.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "results": results,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.run_detection_rule_yaml_tests_response_data_results import RunDetectionRuleYamlTestsResponseDataResults
        d = src_dict.copy()
        results = RunDetectionRuleYamlTestsResponseDataResults.from_dict(d.pop("results"))




        run_detection_rule_yaml_tests_response_data = cls(
            results=results,
        )


        run_detection_rule_yaml_tests_response_data.additional_properties = d
        return run_detection_rule_yaml_tests_response_data

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
