from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ollama_x_client.types import UNSET, Unset

T = TypeVar("T", bound="ContinueConfig")


@_attrs_define
class ContinueConfig:
    """
    Attributes:
        config_json (Union[Unset, str]):  Default: ''.
        config_js (Union[Unset, str]):  Default: ''.
    """

    config_json: Union[Unset, str] = ""
    config_js: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        config_json = self.config_json

        config_js = self.config_js

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config_json is not UNSET:
            field_dict["configJson"] = config_json
        if config_js is not UNSET:
            field_dict["configJs"] = config_js

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        config_json = d.pop("configJson", UNSET)

        config_js = d.pop("configJs", UNSET)

        continue_config = cls(
            config_json=config_json,
            config_js=config_js,
        )

        continue_config.additional_properties = d
        return continue_config

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
