from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.detection_severity_type_1 import DetectionSeverityType1
from ..models.detection_severity_type_0 import DetectionSeverityType0
from ..models.detection_severity_type_6 import DetectionSeverityType6
from ..models.detection_severity_type_3 import DetectionSeverityType3
from ..models.detection_severity_type_7 import DetectionSeverityType7
from dateutil.parser import isoparse
from ..models.detection_severity_type_4 import DetectionSeverityType4
from ..models.detection_severity_type_2 import DetectionSeverityType2
from typing import cast
import datetime
from ..types import UNSET, Unset
from typing import Union
from typing import cast, Union
from ..models.detection_severity_type_5 import DetectionSeverityType5






T = TypeVar("T", bound="DetectionRuleSummary")


@_attrs_define
class DetectionRuleSummary:
    """ 
        Attributes:
            created_at (datetime.datetime):
            description (str):
            enabled (bool):
            id (str):
            name (str):
            prepared_query_id (str):
            query_text (str):
            run_frequency_s (int):
            severity (Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3,
                DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7]): The severity
                of a detection rule. Uses the OCSF severity schema for detection findings. In particular, uses the integer and
                string representations of the severity levels as described in the OCSF schema spec here:
                https://schema.ocsf.io/1.1.0/classes/detection_finding
            tenant_id (str):
            time_range_s (int):
            updated_at (datetime.datetime):
            author_user_id (Union[None, Unset, str]):
            detection_rule_sync_id (Union[None, Unset, str]):
            last_alerted_at (Union[None, Unset, datetime.datetime]):
            sync_key (Union[None, Unset, str]):
     """

    created_at: datetime.datetime
    description: str
    enabled: bool
    id: str
    name: str
    prepared_query_id: str
    query_text: str
    run_frequency_s: int
    severity: Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3, DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7]
    tenant_id: str
    time_range_s: int
    updated_at: datetime.datetime
    author_user_id: Union[None, Unset, str] = UNSET
    detection_rule_sync_id: Union[None, Unset, str] = UNSET
    last_alerted_at: Union[None, Unset, datetime.datetime] = UNSET
    sync_key: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()

        description = self.description

        enabled = self.enabled

        id = self.id

        name = self.name

        prepared_query_id = self.prepared_query_id

        query_text = self.query_text

        run_frequency_s = self.run_frequency_s

        severity: str
        if isinstance(self.severity, DetectionSeverityType0):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType1):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType2):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType3):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType4):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType5):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType6):
            severity = self.severity.value
        else:
            severity = self.severity.value


        tenant_id = self.tenant_id

        time_range_s = self.time_range_s

        updated_at = self.updated_at.isoformat()

        author_user_id: Union[None, Unset, str]
        if isinstance(self.author_user_id, Unset):
            author_user_id = UNSET
        else:
            author_user_id = self.author_user_id

        detection_rule_sync_id: Union[None, Unset, str]
        if isinstance(self.detection_rule_sync_id, Unset):
            detection_rule_sync_id = UNSET
        else:
            detection_rule_sync_id = self.detection_rule_sync_id

        last_alerted_at: Union[None, Unset, str]
        if isinstance(self.last_alerted_at, Unset):
            last_alerted_at = UNSET
        elif isinstance(self.last_alerted_at, datetime.datetime):
            last_alerted_at = self.last_alerted_at.isoformat()
        else:
            last_alerted_at = self.last_alerted_at

        sync_key: Union[None, Unset, str]
        if isinstance(self.sync_key, Unset):
            sync_key = UNSET
        else:
            sync_key = self.sync_key


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "created_at": created_at,
            "description": description,
            "enabled": enabled,
            "id": id,
            "name": name,
            "prepared_query_id": prepared_query_id,
            "query_text": query_text,
            "run_frequency_s": run_frequency_s,
            "severity": severity,
            "tenant_id": tenant_id,
            "time_range_s": time_range_s,
            "updated_at": updated_at,
        })
        if author_user_id is not UNSET:
            field_dict["author_user_id"] = author_user_id
        if detection_rule_sync_id is not UNSET:
            field_dict["detection_rule_sync_id"] = detection_rule_sync_id
        if last_alerted_at is not UNSET:
            field_dict["last_alerted_at"] = last_alerted_at
        if sync_key is not UNSET:
            field_dict["sync_key"] = sync_key

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))




        description = d.pop("description")

        enabled = d.pop("enabled")

        id = d.pop("id")

        name = d.pop("name")

        prepared_query_id = d.pop("prepared_query_id")

        query_text = d.pop("query_text")

        run_frequency_s = d.pop("run_frequency_s")

        def _parse_severity(data: object) -> Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3, DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_0 = DetectionSeverityType0(data)



                return componentsschemas_detection_severity_type_0
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_1 = DetectionSeverityType1(data)



                return componentsschemas_detection_severity_type_1
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_2 = DetectionSeverityType2(data)



                return componentsschemas_detection_severity_type_2
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_3 = DetectionSeverityType3(data)



                return componentsschemas_detection_severity_type_3
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_4 = DetectionSeverityType4(data)



                return componentsschemas_detection_severity_type_4
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_5 = DetectionSeverityType5(data)



                return componentsschemas_detection_severity_type_5
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_6 = DetectionSeverityType6(data)



                return componentsschemas_detection_severity_type_6
            except: # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            componentsschemas_detection_severity_type_7 = DetectionSeverityType7(data)



            return componentsschemas_detection_severity_type_7

        severity = _parse_severity(d.pop("severity"))


        tenant_id = d.pop("tenant_id")

        time_range_s = d.pop("time_range_s")

        updated_at = isoparse(d.pop("updated_at"))




        def _parse_author_user_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        author_user_id = _parse_author_user_id(d.pop("author_user_id", UNSET))


        def _parse_detection_rule_sync_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        detection_rule_sync_id = _parse_detection_rule_sync_id(d.pop("detection_rule_sync_id", UNSET))


        def _parse_last_alerted_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_alerted_at_type_0 = isoparse(data)



                return last_alerted_at_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_alerted_at = _parse_last_alerted_at(d.pop("last_alerted_at", UNSET))


        def _parse_sync_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sync_key = _parse_sync_key(d.pop("sync_key", UNSET))


        detection_rule_summary = cls(
            created_at=created_at,
            description=description,
            enabled=enabled,
            id=id,
            name=name,
            prepared_query_id=prepared_query_id,
            query_text=query_text,
            run_frequency_s=run_frequency_s,
            severity=severity,
            tenant_id=tenant_id,
            time_range_s=time_range_s,
            updated_at=updated_at,
            author_user_id=author_user_id,
            detection_rule_sync_id=detection_rule_sync_id,
            last_alerted_at=last_alerted_at,
            sync_key=sync_key,
        )


        detection_rule_summary.additional_properties = d
        return detection_rule_summary

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
