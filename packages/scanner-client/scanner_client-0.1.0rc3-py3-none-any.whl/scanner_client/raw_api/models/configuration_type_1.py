from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.slack_configuration import SlackConfiguration





T = TypeVar("T", bound="ConfigurationType1")


@_attrs_define
class ConfigurationType1:
    """ 
        Attributes:
            slack (SlackConfiguration): Represents Slack configuration, but only with fields that are safe to share in
                public, i.e. secrets info removed.
     """

    slack: 'SlackConfiguration'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.slack_configuration import SlackConfiguration
        slack = self.slack.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "Slack": slack,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.slack_configuration import SlackConfiguration
        d = src_dict.copy()
        slack = SlackConfiguration.from_dict(d.pop("Slack"))




        configuration_type_1 = cls(
            slack=slack,
        )

        return configuration_type_1

