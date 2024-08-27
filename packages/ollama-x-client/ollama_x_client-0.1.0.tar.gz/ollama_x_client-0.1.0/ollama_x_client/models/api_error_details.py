from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ollama_x_client.models.api_error_details_code import APIErrorDetailsCode

T = TypeVar("T", bound="APIErrorDetails")


@_attrs_define
class APIErrorDetails:
    """
    Attributes:
        code (APIErrorDetailsCode):
        message (str):
    """

    code: APIErrorDetailsCode
    message: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        code = self.code.value

        message = self.message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        code = APIErrorDetailsCode(d.pop("code"))

        message = d.pop("message")

        api_error_details = cls(
            code=code,
            message=message,
        )

        api_error_details.additional_properties = d
        return api_error_details

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
