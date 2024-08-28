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
from typing import Dict
from ..models.detection_severity_type_2 import DetectionSeverityType2
from typing import cast
from ..types import UNSET, Unset
from typing import Union
from typing import cast, Union
from ..models.detection_severity_type_5 import DetectionSeverityType5

if TYPE_CHECKING:
  from ..models.perms_by_role_for_rbac_detection_rule_permission_type import PermsByRoleForRbacDetectionRulePermissionType





T = TypeVar("T", bound="CreateDetectionRuleRequestData")


@_attrs_define
class CreateDetectionRuleRequestData:
    """ 
        Attributes:
            description (str):
            event_sink_ids (List[str]):
            name (str):
            query_text (str):
            run_frequency_s (int):
            tenant_id (str):
            time_range_s (int):
            enabled (Union[Unset, bool]):  Default: True.
            severity (Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3,
                DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7, Unset]): The
                severity of a detection rule. Uses the OCSF severity schema for detection findings. In particular, uses the
                integer and string representations of the severity levels as described in the OCSF schema spec here:
                https://schema.ocsf.io/1.1.0/classes/detection_finding Default: DetectionSeverityType0.UNKNOWN.
            starting_permissions (Union['PermsByRoleForRbacDetectionRulePermissionType', None, Unset]):
            sync_key (Union[None, Unset, str]):
     """

    description: str
    event_sink_ids: List[str]
    name: str
    query_text: str
    run_frequency_s: int
    tenant_id: str
    time_range_s: int
    enabled: Union[Unset, bool] = True
    severity: Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3, DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7, Unset] = DetectionSeverityType0.UNKNOWN
    starting_permissions: Union['PermsByRoleForRbacDetectionRulePermissionType', None, Unset] = UNSET
    sync_key: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.perms_by_role_for_rbac_detection_rule_permission_type import PermsByRoleForRbacDetectionRulePermissionType
        description = self.description

        event_sink_ids = self.event_sink_ids



        name = self.name

        query_text = self.query_text

        run_frequency_s = self.run_frequency_s

        tenant_id = self.tenant_id

        time_range_s = self.time_range_s

        enabled = self.enabled

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


        starting_permissions: Union[Dict[str, Any], None, Unset]
        if isinstance(self.starting_permissions, Unset):
            starting_permissions = UNSET
        elif isinstance(self.starting_permissions, PermsByRoleForRbacDetectionRulePermissionType):
            starting_permissions = self.starting_permissions.to_dict()
        else:
            starting_permissions = self.starting_permissions

        sync_key: Union[None, Unset, str]
        if isinstance(self.sync_key, Unset):
            sync_key = UNSET
        else:
            sync_key = self.sync_key


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "description": description,
            "event_sink_ids": event_sink_ids,
            "name": name,
            "query_text": query_text,
            "run_frequency_s": run_frequency_s,
            "tenant_id": tenant_id,
            "time_range_s": time_range_s,
        })
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if severity is not UNSET:
            field_dict["severity"] = severity
        if starting_permissions is not UNSET:
            field_dict["starting_permissions"] = starting_permissions
        if sync_key is not UNSET:
            field_dict["sync_key"] = sync_key

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.perms_by_role_for_rbac_detection_rule_permission_type import PermsByRoleForRbacDetectionRulePermissionType
        d = src_dict.copy()
        description = d.pop("description")

        event_sink_ids = cast(List[str], d.pop("event_sink_ids"))


        name = d.pop("name")

        query_text = d.pop("query_text")

        run_frequency_s = d.pop("run_frequency_s")

        tenant_id = d.pop("tenant_id")

        time_range_s = d.pop("time_range_s")

        enabled = d.pop("enabled", UNSET)

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


        def _parse_starting_permissions(data: object) -> Union['PermsByRoleForRbacDetectionRulePermissionType', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                starting_permissions_type_0 = PermsByRoleForRbacDetectionRulePermissionType.from_dict(data)



                return starting_permissions_type_0
            except: # noqa: E722
                pass
            return cast(Union['PermsByRoleForRbacDetectionRulePermissionType', None, Unset], data)

        starting_permissions = _parse_starting_permissions(d.pop("starting_permissions", UNSET))


        def _parse_sync_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sync_key = _parse_sync_key(d.pop("sync_key", UNSET))


        create_detection_rule_request_data = cls(
            description=description,
            event_sink_ids=event_sink_ids,
            name=name,
            query_text=query_text,
            run_frequency_s=run_frequency_s,
            tenant_id=tenant_id,
            time_range_s=time_range_s,
            enabled=enabled,
            severity=severity,
            starting_permissions=starting_permissions,
            sync_key=sync_key,
        )


        create_detection_rule_request_data.additional_properties = d
        return create_detection_rule_request_data

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
