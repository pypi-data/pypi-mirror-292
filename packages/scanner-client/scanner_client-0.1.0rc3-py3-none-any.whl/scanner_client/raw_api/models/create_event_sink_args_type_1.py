from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.create_webhook_event_sink_args import CreateWebhookEventSinkArgs





T = TypeVar("T", bound="CreateEventSinkArgsType1")


@_attrs_define
class CreateEventSinkArgsType1:
    """ 
        Attributes:
            webhook (CreateWebhookEventSinkArgs):
     """

    webhook: 'CreateWebhookEventSinkArgs'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.create_webhook_event_sink_args import CreateWebhookEventSinkArgs
        webhook = self.webhook.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "Webhook": webhook,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_webhook_event_sink_args import CreateWebhookEventSinkArgs
        d = src_dict.copy()
        webhook = CreateWebhookEventSinkArgs.from_dict(d.pop("Webhook"))




        create_event_sink_args_type_1 = cls(
            webhook=webhook,
        )

        return create_event_sink_args_type_1

