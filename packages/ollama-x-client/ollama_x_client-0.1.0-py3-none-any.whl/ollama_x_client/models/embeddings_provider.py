from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ollama_x_client.models.embeddings_provider_provider import EmbeddingsProviderProvider
from ollama_x_client.types import UNSET, Unset

if TYPE_CHECKING:
    from ollama_x_client.models.request_options import RequestOptions


T = TypeVar("T", bound="EmbeddingsProvider")


@_attrs_define
class EmbeddingsProvider:
    """
    Attributes:
        provider (Union[Unset, EmbeddingsProviderProvider]): Provider name Default: EmbeddingsProviderProvider.OLLAMA.
        model (Union[None, Unset, str]): Model name
        api_base (Union[None, Unset, str]): API base
        api_key (Union[None, Unset, str]): API key
        request_options (Union[Unset, RequestOptions]):
    """

    provider: Union[Unset, EmbeddingsProviderProvider] = EmbeddingsProviderProvider.OLLAMA
    model: Union[None, Unset, str] = UNSET
    api_base: Union[None, Unset, str] = UNSET
    api_key: Union[None, Unset, str] = UNSET
    request_options: Union[Unset, "RequestOptions"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        provider: Union[Unset, str] = UNSET
        if not isinstance(self.provider, Unset):
            provider = self.provider.value

        model: Union[None, Unset, str]
        if isinstance(self.model, Unset):
            model = UNSET
        else:
            model = self.model

        api_base: Union[None, Unset, str]
        if isinstance(self.api_base, Unset):
            api_base = UNSET
        else:
            api_base = self.api_base

        api_key: Union[None, Unset, str]
        if isinstance(self.api_key, Unset):
            api_key = UNSET
        else:
            api_key = self.api_key

        request_options: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.request_options, Unset):
            request_options = self.request_options.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if provider is not UNSET:
            field_dict["provider"] = provider
        if model is not UNSET:
            field_dict["model"] = model
        if api_base is not UNSET:
            field_dict["apiBase"] = api_base
        if api_key is not UNSET:
            field_dict["apiKey"] = api_key
        if request_options is not UNSET:
            field_dict["requestOptions"] = request_options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ollama_x_client.models.request_options import RequestOptions

        d = src_dict.copy()
        _provider = d.pop("provider", UNSET)
        provider: Union[Unset, EmbeddingsProviderProvider]
        if isinstance(_provider, Unset):
            provider = UNSET
        else:
            provider = EmbeddingsProviderProvider(_provider)

        def _parse_model(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        model = _parse_model(d.pop("model", UNSET))

        def _parse_api_base(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        api_base = _parse_api_base(d.pop("apiBase", UNSET))

        def _parse_api_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        api_key = _parse_api_key(d.pop("apiKey", UNSET))

        _request_options = d.pop("requestOptions", UNSET)
        request_options: Union[Unset, RequestOptions]
        if isinstance(_request_options, Unset):
            request_options = UNSET
        else:
            request_options = RequestOptions.from_dict(_request_options)

        embeddings_provider = cls(
            provider=provider,
            model=model,
            api_base=api_base,
            api_key=api_key,
            request_options=request_options,
        )

        embeddings_provider.additional_properties = d
        return embeddings_provider

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
