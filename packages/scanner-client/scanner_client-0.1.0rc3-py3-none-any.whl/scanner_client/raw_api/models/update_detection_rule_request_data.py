from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from ..models.detection_severity_type_1 import DetectionSeverityType1
from ..models.detection_severity_type_0 import DetectionSeverityType0
from ..models.detection_severity_type_6 import DetectionSeverityType6
from ..models.detection_severity_type_3 import DetectionSeverityType3
from ..models.detection_severity_type_7 import DetectionSeverityType7
from ..models.detection_severity_type_4 import DetectionSeverityType4
from ..models.detection_severity_type_2 import DetectionSeverityType2
from ..types import UNSET, Unset
from typing import Union
from typing import cast, Union
from ..models.detection_severity_type_5 import DetectionSeverityType5






T = TypeVar("T", bound="UpdateDetectionRuleRequestData")


@_attrs_define
class UpdateDetectionRuleRequestData:
    """ 
        Attributes:
            id (str):
            description (Union[Unset, str]): This implements a type which describes whether a value should be updated or
                not, that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
            enabled (Union[Unset, bool]): This implements a type which describes whether a value should be updated or not,
                that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
            event_sink_ids (Union[List[str], Unset]): This implements a type which describes whether a value should be
                updated or not, that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
            name (Union[Unset, str]): This implements a type which describes whether a value should be updated or not,
                that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
            query_text (Union[Unset, str]): This implements a type which describes whether a value should be updated or not,
                that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
            run_frequency_s (Union[Unset, int]): This implements a type which describes whether a value should be updated or
                not, that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
            severity (Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3,
                DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7, Unset]): The
                severity of a detection rule. Uses the OCSF severity schema for detection findings. In particular, uses the
                integer and string representations of the severity levels as described in the OCSF schema spec here:
                https://schema.ocsf.io/1.1.0/classes/detection_finding
            sync_key (Union[None, Unset, str]): This implements a type which describes whether a value should be updated or
                not, that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
            time_range_s (Union[Unset, int]): This implements a type which describes whether a value should be updated or
                not, that's used in most update routes in the API.

                This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
                Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

                Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
     """

    id: str
    description: Union[Unset, str] = UNSET
    enabled: Union[Unset, bool] = UNSET
    event_sink_ids: Union[List[str], Unset] = UNSET
    name: Union[Unset, str] = UNSET
    query_text: Union[Unset, str] = UNSET
    run_frequency_s: Union[Unset, int] = UNSET
    severity: Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3, DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7, Unset] = UNSET
    sync_key: Union[None, Unset, str] = UNSET
    time_range_s: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        description: Union[Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        enabled: Union[Unset, bool]
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        event_sink_ids: Union[List[str], Unset]
        if isinstance(self.event_sink_ids, Unset):
            event_sink_ids = UNSET
        else:
            event_sink_ids = self.event_sink_ids




        name: Union[Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        query_text: Union[Unset, str]
        if isinstance(self.query_text, Unset):
            query_text = UNSET
        else:
            query_text = self.query_text

        run_frequency_s: Union[Unset, int]
        if isinstance(self.run_frequency_s, Unset):
            run_frequency_s = UNSET
        else:
            run_frequency_s = self.run_frequency_s

        severity: Union[Unset, str]
        if isinstance(self.severity, Unset):
            severity = UNSET
        elif isinstance(self.severity, DetectionSeverityType0):
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


        sync_key: Union[None, Unset, str]
        if isinstance(self.sync_key, Unset):
            sync_key = UNSET
        else:
            sync_key = self.sync_key

        time_range_s: Union[Unset, int]
        if isinstance(self.time_range_s, Unset):
            time_range_s = UNSET
        else:
            time_range_s = self.time_range_s


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if event_sink_ids is not UNSET:
            field_dict["event_sink_ids"] = event_sink_ids
        if name is not UNSET:
            field_dict["name"] = name
        if query_text is not UNSET:
            field_dict["query_text"] = query_text
        if run_frequency_s is not UNSET:
            field_dict["run_frequency_s"] = run_frequency_s
        if severity is not UNSET:
            field_dict["severity"] = severity
        if sync_key is not UNSET:
            field_dict["sync_key"] = sync_key
        if time_range_s is not UNSET:
            field_dict["time_range_s"] = time_range_s

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        def _parse_description(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_enabled(data: object) -> Union[Unset, bool]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, bool], data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))


        def _parse_event_sink_ids(data: object) -> Union[List[str], Unset]:
            if isinstance(data, Unset):
                return data
            if not isinstance(data, list):
                raise TypeError()
            componentsschemas_update_value_for_array_of_event_sink_id_type_0 = cast(List[str], data)

            return componentsschemas_update_value_for_array_of_event_sink_id_type_0

        event_sink_ids = _parse_event_sink_ids(d.pop("event_sink_ids", UNSET))


        def _parse_name(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_query_text(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        query_text = _parse_query_text(d.pop("query_text", UNSET))


        def _parse_run_frequency_s(data: object) -> Union[Unset, int]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, int], data)

        run_frequency_s = _parse_run_frequency_s(d.pop("run_frequency_s", UNSET))


        def _parse_severity(data: object) -> Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3, DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7, Unset]:
            if isinstance(data, Unset):
                return data
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

        severity = _parse_severity(d.pop("severity", UNSET))


        def _parse_sync_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sync_key = _parse_sync_key(d.pop("sync_key", UNSET))


        def _parse_time_range_s(data: object) -> Union[Unset, int]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, int], data)

        time_range_s = _parse_time_range_s(d.pop("time_range_s", UNSET))


        update_detection_rule_request_data = cls(
            id=id,
            description=description,
            enabled=enabled,
            event_sink_ids=event_sink_ids,
            name=name,
            query_text=query_text,
            run_frequency_s=run_frequency_s,
            severity=severity,
            sync_key=sync_key,
            time_range_s=time_range_s,
        )


        update_detection_rule_request_data.additional_properties = d
        return update_detection_rule_request_data

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
