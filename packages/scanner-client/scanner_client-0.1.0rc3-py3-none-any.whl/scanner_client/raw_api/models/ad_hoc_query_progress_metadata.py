from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="AdHocQueryProgressMetadata")


@_attrs_define
class AdHocQueryProgressMetadata:
    """ 
        Attributes:
            n_bytes_scanned (int):
     """

    n_bytes_scanned: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        n_bytes_scanned = self.n_bytes_scanned


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "n_bytes_scanned": n_bytes_scanned,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        n_bytes_scanned = d.pop("n_bytes_scanned")

        ad_hoc_query_progress_metadata = cls(
            n_bytes_scanned=n_bytes_scanned,
        )


        ad_hoc_query_progress_metadata.additional_properties = d
        return ad_hoc_query_progress_metadata

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
