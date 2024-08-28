from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.update_slack_integration_args import UpdateSlackIntegrationArgs





T = TypeVar("T", bound="UpdateIntegrationArgsType0")


@_attrs_define
class UpdateIntegrationArgsType0:
    """ 
        Attributes:
            slack (UpdateSlackIntegrationArgs):
     """

    slack: 'UpdateSlackIntegrationArgs'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.update_slack_integration_args import UpdateSlackIntegrationArgs
        slack = self.slack.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "Slack": slack,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_slack_integration_args import UpdateSlackIntegrationArgs
        d = src_dict.copy()
        slack = UpdateSlackIntegrationArgs.from_dict(d.pop("Slack"))




        update_integration_args_type_0 = cls(
            slack=slack,
        )

        return update_integration_args_type_0

