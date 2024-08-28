from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="CreateSlackIntegrationArgs")


@_attrs_define
class CreateSlackIntegrationArgs:
    """ 
        Attributes:
            channel (str):
            slack_oauth_code (str):
     """

    channel: str
    slack_oauth_code: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        channel = self.channel

        slack_oauth_code = self.slack_oauth_code


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "channel": channel,
            "slack_oauth_code": slack_oauth_code,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        channel = d.pop("channel")

        slack_oauth_code = d.pop("slack_oauth_code")

        create_slack_integration_args = cls(
            channel=channel,
            slack_oauth_code=slack_oauth_code,
        )


        create_slack_integration_args.additional_properties = d
        return create_slack_integration_args

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
