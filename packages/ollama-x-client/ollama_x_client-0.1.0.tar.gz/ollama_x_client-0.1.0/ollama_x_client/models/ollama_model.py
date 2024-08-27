from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ollama_x_client.models.ollama_model_provider import OllamaModelProvider
from ollama_x_client.types import UNSET, Unset

if TYPE_CHECKING:
    from ollama_x_client.models.model_request_options import ModelRequestOptions


T = TypeVar("T", bound="OllamaModel")


@_attrs_define
class OllamaModel:
    """
    Attributes:
        model (Union[Unset, str]): Model name Default: 'AUTODETECT'.
        title (Union[Unset, str]): Model title Default: 'Model'.
        provider (Union[Unset, OllamaModelProvider]): Provider Default: OllamaModelProvider.OLLAMA.
        api_key (Union[None, Unset, str]): API key
        api_base (Union[None, Unset, str]): OAPI base
        request_options (Union[Unset, ModelRequestOptions]):
    """

    model: Union[Unset, str] = "AUTODETECT"
    title: Union[Unset, str] = "Model"
    provider: Union[Unset, OllamaModelProvider] = OllamaModelProvider.OLLAMA
    api_key: Union[None, Unset, str] = UNSET
    api_base: Union[None, Unset, str] = UNSET
    request_options: Union[Unset, "ModelRequestOptions"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        model = self.model

        title = self.title

        provider: Union[Unset, str] = UNSET
        if not isinstance(self.provider, Unset):
            provider = self.provider.value

        api_key: Union[None, Unset, str]
        if isinstance(self.api_key, Unset):
            api_key = UNSET
        else:
            api_key = self.api_key

        api_base: Union[None, Unset, str]
        if isinstance(self.api_base, Unset):
            api_base = UNSET
        else:
            api_base = self.api_base

        request_options: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.request_options, Unset):
            request_options = self.request_options.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model is not UNSET:
            field_dict["model"] = model
        if title is not UNSET:
            field_dict["title"] = title
        if provider is not UNSET:
            field_dict["provider"] = provider
        if api_key is not UNSET:
            field_dict["apiKey"] = api_key
        if api_base is not UNSET:
            field_dict["apiBase"] = api_base
        if request_options is not UNSET:
            field_dict["requestOptions"] = request_options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ollama_x_client.models.model_request_options import ModelRequestOptions

        d = src_dict.copy()
        model = d.pop("model", UNSET)

        title = d.pop("title", UNSET)

        _provider = d.pop("provider", UNSET)
        provider: Union[Unset, OllamaModelProvider]
        if isinstance(_provider, Unset):
            provider = UNSET
        else:
            provider = OllamaModelProvider(_provider)

        def _parse_api_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        api_key = _parse_api_key(d.pop("apiKey", UNSET))

        def _parse_api_base(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        api_base = _parse_api_base(d.pop("apiBase", UNSET))

        _request_options = d.pop("requestOptions", UNSET)
        request_options: Union[Unset, ModelRequestOptions]
        if isinstance(_request_options, Unset):
            request_options = UNSET
        else:
            request_options = ModelRequestOptions.from_dict(_request_options)

        ollama_model = cls(
            model=model,
            title=title,
            provider=provider,
            api_key=api_key,
            api_base=api_base,
            request_options=request_options,
        )

        ollama_model.additional_properties = d
        return ollama_model

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
