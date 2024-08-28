from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, Union
from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.log_event_id import LogEventId
  from ..models.ad_hoc_row_item_columns import AdHocRowItemColumns





T = TypeVar("T", bound="AdHocRowItem")


@_attrs_define
class AdHocRowItem:
    """ 
        Attributes:
            columns (AdHocRowItemColumns):
            row_id (Union['LogEventId', int]):
     """

    columns: 'AdHocRowItemColumns'
    row_id: Union['LogEventId', int]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.log_event_id import LogEventId
        from ..models.ad_hoc_row_item_columns import AdHocRowItemColumns
        columns = self.columns.to_dict()

        row_id: Union[Dict[str, Any], int]
        if isinstance(self.row_id, LogEventId):
            row_id = self.row_id.to_dict()
        else:
            row_id = self.row_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "columns": columns,
            "row_id": row_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.log_event_id import LogEventId
        from ..models.ad_hoc_row_item_columns import AdHocRowItemColumns
        d = src_dict.copy()
        columns = AdHocRowItemColumns.from_dict(d.pop("columns"))




        def _parse_row_id(data: object) -> Union['LogEventId', int]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_any_row_id_json_type_0 = LogEventId.from_dict(data)



                return componentsschemas_any_row_id_json_type_0
            except: # noqa: E722
                pass
            return cast(Union['LogEventId', int], data)

        row_id = _parse_row_id(d.pop("row_id"))


        ad_hoc_row_item = cls(
            columns=columns,
            row_id=row_id,
        )


        ad_hoc_row_item.additional_properties = d
        return ad_hoc_row_item

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
