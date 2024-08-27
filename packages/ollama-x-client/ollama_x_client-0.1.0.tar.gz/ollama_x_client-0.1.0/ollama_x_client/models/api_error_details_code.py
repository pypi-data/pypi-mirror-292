from enum import Enum


class APIErrorDetailsCode(str, Enum):
    ACCESSDENIED = "AccessDenied"

    def __str__(self) -> str:
        return str(self.value)
