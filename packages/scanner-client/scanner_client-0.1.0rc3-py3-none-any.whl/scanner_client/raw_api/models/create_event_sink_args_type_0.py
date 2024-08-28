from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.create_slack_event_sink_args import CreateSlackEventSinkArgs





T = TypeVar("T", bound="CreateEventSinkArgsType0")


@_attrs_define
class CreateEventSinkArgsType0:
    """ 
        Attributes:
            slack (CreateSlackEventSinkArgs):
     """

    slack: 'CreateSlackEventSinkArgs'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.create_slack_event_sink_args import CreateSlackEventSinkArgs
        slack = self.slack.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "Slack": slack,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_slack_event_sink_args import CreateSlackEventSinkArgs
        d = src_dict.copy()
        slack = CreateSlackEventSinkArgs.from_dict(d.pop("Slack"))




        create_event_sink_args_type_0 = cls(
            slack=slack,
        )

        return create_event_sink_args_type_0

