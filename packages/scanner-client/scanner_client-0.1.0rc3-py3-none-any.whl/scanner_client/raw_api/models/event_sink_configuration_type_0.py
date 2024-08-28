from enum import Enum


class EventSinkConfigurationType0(str, Enum):
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
