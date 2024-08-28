from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.tines_configuration import TinesConfiguration





T = TypeVar("T", bound="ConfigurationType2")


@_attrs_define
class ConfigurationType2:
    """ 
        Attributes:
            tines (TinesConfiguration): Represents Tines configuration, but only with fields that are safe to share in
                public, i.e. secrets info removed.
     """

    tines: 'TinesConfiguration'


    def to_dict(self) -> Dict[str, Any]:
        from ..models.tines_configuration import TinesConfiguration
        tines = self.tines.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "Tines": tines,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.tines_configuration import TinesConfiguration
        d = src_dict.copy()
        tines = TinesConfiguration.from_dict(d.pop("Tines"))




        configuration_type_2 = cls(
            tines=tines,
        )

        return configuration_type_2

