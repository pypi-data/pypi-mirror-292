from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Dict
from typing import cast
from typing import Union
from ..types import UNSET, Unset
from typing import cast, Union

if TYPE_CHECKING:
  from ..models.log_event_id import LogEventId





T = TypeVar("T", bound="StartAdHocQueryRequestData")


@_attrs_define
class StartAdHocQueryRequestData:
    """ 
        Attributes:
            query (str):
            end_leid (Union['LogEventId', None, Unset]):
            end_time (Union[None, Unset, str]):
            max_rows (Union[Unset, int]):  Default: 1000.
            scan_back_to_front (Union[None, Unset, bool]):
            start_leid (Union['LogEventId', None, Unset]):
            start_time (Union[None, Unset, str]):
     """

    query: str
    end_leid: Union['LogEventId', None, Unset] = UNSET
    end_time: Union[None, Unset, str] = UNSET
    max_rows: Union[Unset, int] = 1000
    scan_back_to_front: Union[None, Unset, bool] = UNSET
    start_leid: Union['LogEventId', None, Unset] = UNSET
    start_time: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.log_event_id import LogEventId
        query = self.query

        end_leid: Union[Dict[str, Any], None, Unset]
        if isinstance(self.end_leid, Unset):
            end_leid = UNSET
        elif isinstance(self.end_leid, LogEventId):
            end_leid = self.end_leid.to_dict()
        else:
            end_leid = self.end_leid

        end_time: Union[None, Unset, str]
        if isinstance(self.end_time, Unset):
            end_time = UNSET
        else:
            end_time = self.end_time

        max_rows = self.max_rows

        scan_back_to_front: Union[None, Unset, bool]
        if isinstance(self.scan_back_to_front, Unset):
            scan_back_to_front = UNSET
        else:
            scan_back_to_front = self.scan_back_to_front

        start_leid: Union[Dict[str, Any], None, Unset]
        if isinstance(self.start_leid, Unset):
            start_leid = UNSET
        elif isinstance(self.start_leid, LogEventId):
            start_leid = self.start_leid.to_dict()
        else:
            start_leid = self.start_leid

        start_time: Union[None, Unset, str]
        if isinstance(self.start_time, Unset):
            start_time = UNSET
        else:
            start_time = self.start_time


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "query": query,
        })
        if end_leid is not UNSET:
            field_dict["end_leid"] = end_leid
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if max_rows is not UNSET:
            field_dict["max_rows"] = max_rows
        if scan_back_to_front is not UNSET:
            field_dict["scan_back_to_front"] = scan_back_to_front
        if start_leid is not UNSET:
            field_dict["start_leid"] = start_leid
        if start_time is not UNSET:
            field_dict["start_time"] = start_time

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.log_event_id import LogEventId
        d = src_dict.copy()
        query = d.pop("query")

        def _parse_end_leid(data: object) -> Union['LogEventId', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                end_leid_type_0 = LogEventId.from_dict(data)



                return end_leid_type_0
            except: # noqa: E722
                pass
            return cast(Union['LogEventId', None, Unset], data)

        end_leid = _parse_end_leid(d.pop("end_leid", UNSET))


        def _parse_end_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        end_time = _parse_end_time(d.pop("end_time", UNSET))


        max_rows = d.pop("max_rows", UNSET)

        def _parse_scan_back_to_front(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        scan_back_to_front = _parse_scan_back_to_front(d.pop("scan_back_to_front", UNSET))


        def _parse_start_leid(data: object) -> Union['LogEventId', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                start_leid_type_0 = LogEventId.from_dict(data)



                return start_leid_type_0
            except: # noqa: E722
                pass
            return cast(Union['LogEventId', None, Unset], data)

        start_leid = _parse_start_leid(d.pop("start_leid", UNSET))


        def _parse_start_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        start_time = _parse_start_time(d.pop("start_time", UNSET))


        start_ad_hoc_query_request_data = cls(
            query=query,
            end_leid=end_leid,
            end_time=end_time,
            max_rows=max_rows,
            scan_back_to_front=scan_back_to_front,
            start_leid=start_leid,
            start_time=start_time,
        )


        start_ad_hoc_query_request_data.additional_properties = d
        return start_ad_hoc_query_request_data

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
