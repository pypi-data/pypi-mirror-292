from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ollama_x_client.models.api_error_details import APIErrorDetails


T = TypeVar("T", bound="APIErrorAccessDenied")


@_attrs_define
class APIErrorAccessDenied:
    """
    Attributes:
        detail (APIErrorDetails):
    """

    detail: "APIErrorDetails"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        detail = self.detail.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detail": detail,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ollama_x_client.models.api_error_details import APIErrorDetails

        d = src_dict.copy()
        detail = APIErrorDetails.from_dict(d.pop("detail"))

        api_error_access_denied = cls(
            detail=detail,
        )

        api_error_access_denied.additional_properties = d
        return api_error_access_denied

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
