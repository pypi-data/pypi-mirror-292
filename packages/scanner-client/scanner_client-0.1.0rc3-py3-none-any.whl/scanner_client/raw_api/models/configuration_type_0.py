from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.github_configuration import GithubConfiguration





T = TypeVar("T", bound="ConfigurationType0")


@_attrs_define
class ConfigurationType0:
    """ 
        Attributes:
            github (GithubConfiguration):
     """

    github: 'GithubConfiguration'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.github_configuration import GithubConfiguration
        github = self.github.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "Github": github,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.github_configuration import GithubConfiguration
        d = src_dict.copy()
        github = GithubConfiguration.from_dict(d.pop("Github"))




        configuration_type_0 = cls(
            github=github,
        )

        return configuration_type_0

