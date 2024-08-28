from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.update_webhook_event_sink_args import UpdateWebhookEventSinkArgs





T = TypeVar("T", bound="UpdateEventSinkArgsType1")


@_attrs_define
class UpdateEventSinkArgsType1:
    """ 
        Attributes:
            webhook (UpdateWebhookEventSinkArgs):
     """

    webhook: 'UpdateWebhookEventSinkArgs'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.update_webhook_event_sink_args import UpdateWebhookEventSinkArgs
        webhook = self.webhook.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "Webhook": webhook,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_webhook_event_sink_args import UpdateWebhookEventSinkArgs
        d = src_dict.copy()
        webhook = UpdateWebhookEventSinkArgs.from_dict(d.pop("Webhook"))




        update_event_sink_args_type_1 = cls(
            webhook=webhook,
        )

        return update_event_sink_args_type_1

