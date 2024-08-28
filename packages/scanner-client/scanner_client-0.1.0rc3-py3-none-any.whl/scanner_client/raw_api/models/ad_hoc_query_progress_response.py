from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.ad_hoc_query_progress_metadata import AdHocQueryProgressMetadata
  from ..models.ad_hoc_table_result import AdHocTableResult





T = TypeVar("T", bound="AdHocQueryProgressResponse")


@_attrs_define
class AdHocQueryProgressResponse:
    """ 
        Attributes:
            is_completed (bool):
            metadata (AdHocQueryProgressMetadata):
            results (AdHocTableResult):
     """

    is_completed: bool
    metadata: 'AdHocQueryProgressMetadata'
    results: 'AdHocTableResult'
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.ad_hoc_query_progress_metadata import AdHocQueryProgressMetadata
        from ..models.ad_hoc_table_result import AdHocTableResult
        is_completed = self.is_completed

        metadata = self.metadata.to_dict()

        results = self.results.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "is_completed": is_completed,
            "metadata": metadata,
            "results": results,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.ad_hoc_query_progress_metadata import AdHocQueryProgressMetadata
        from ..models.ad_hoc_table_result import AdHocTableResult
        d = src_dict.copy()
        is_completed = d.pop("is_completed")

        metadata = AdHocQueryProgressMetadata.from_dict(d.pop("metadata"))




        results = AdHocTableResult.from_dict(d.pop("results"))




        ad_hoc_query_progress_response = cls(
            is_completed=is_completed,
            metadata=metadata,
            results=results,
        )


        ad_hoc_query_progress_response.additional_properties = d
        return ad_hoc_query_progress_response

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
