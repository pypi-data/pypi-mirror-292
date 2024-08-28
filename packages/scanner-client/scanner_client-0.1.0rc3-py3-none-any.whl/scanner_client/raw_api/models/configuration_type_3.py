from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.webhook_configuration import WebhookConfiguration





T = TypeVar("T", bound="ConfigurationType3")


@_attrs_define
class ConfigurationType3:
    """ 
        Attributes:
            webhook (WebhookConfiguration): Represents configuration to send messages to a webhook.
     """

    webhook: 'WebhookConfiguration'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.webhook_configuration import WebhookConfiguration
        webhook = self.webhook.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "Webhook": webhook,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.webhook_configuration import WebhookConfiguration
        d = src_dict.copy()
        webhook = WebhookConfiguration.from_dict(d.pop("Webhook"))




        configuration_type_3 = cls(
            webhook=webhook,
        )

        return configuration_type_3

