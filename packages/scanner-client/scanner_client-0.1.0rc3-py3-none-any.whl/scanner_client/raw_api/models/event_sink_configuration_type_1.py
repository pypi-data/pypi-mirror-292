from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.slack_configuration import SlackConfiguration


T = TypeVar("T", bound="EventSinkConfigurationType1")


@_attrs_define
class EventSinkConfigurationType1:
    """
    Attributes:
        slack (SlackConfiguration): Represents Slack configuration, but only with fields that are safe to share in
            public, i.e. secrets info removed.
    """

    slack: "SlackConfiguration"

    def to_dict(self) -> Dict[str, Any]:
        slack = self.slack.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "Slack": slack,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.slack_configuration import SlackConfiguration

        d = src_dict.copy()
        slack = SlackConfiguration.from_dict(d.pop("Slack"))

        event_sink_configuration_type_1 = cls(
            slack=slack,
        )

        return event_sink_configuration_type_1
