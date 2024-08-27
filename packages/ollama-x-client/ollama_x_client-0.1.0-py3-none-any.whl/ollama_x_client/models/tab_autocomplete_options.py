from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ollama_x_client.models.tab_autocomplete_options_multiline_completions_type_0 import TabAutocompleteOptionsMultilineCompletionsType0
from ollama_x_client.types import UNSET, Unset

T = TypeVar("T", bound="TabAutocompleteOptions")


@_attrs_define
class TabAutocompleteOptions:
    """
    Attributes:
        disable (Union[None, Unset, bool]): Disable autocomplete
        use_copy_buffer (Union[None, Unset, bool]): Use copy buffer data in query
        use_file_suffix (Union[None, Unset, bool]): Use file suffix in query
        max_prompt_tokens (Union[None, Unset, int]): Max tokens in query
        debounce_delay (Union[None, Unset, int]): Time delay after last keystroke
        max_suffix_percentage (Union[None, Unset, int]): Max suffix percentage
        prefix_percentage (Union[None, Unset, int]): Prefix percentage
        template (Union[None, Unset, str]): Template
        multiline_completions (Union[None, TabAutocompleteOptionsMultilineCompletionsType0, Unset]): Multiline
            completions
        use_cache (Union[None, Unset, bool]): Use cache
        only_my_code (Union[None, Unset, bool]): Only my code
        use_other_files (Union[None, Unset, bool]): Use other files
        disable_in_files (Union[List[str], None, Unset]): Disable in files
    """

    disable: Union[None, Unset, bool] = UNSET
    use_copy_buffer: Union[None, Unset, bool] = UNSET
    use_file_suffix: Union[None, Unset, bool] = UNSET
    max_prompt_tokens: Union[None, Unset, int] = UNSET
    debounce_delay: Union[None, Unset, int] = UNSET
    max_suffix_percentage: Union[None, Unset, int] = UNSET
    prefix_percentage: Union[None, Unset, int] = UNSET
    template: Union[None, Unset, str] = UNSET
    multiline_completions: Union[None, TabAutocompleteOptionsMultilineCompletionsType0, Unset] = UNSET
    use_cache: Union[None, Unset, bool] = UNSET
    only_my_code: Union[None, Unset, bool] = UNSET
    use_other_files: Union[None, Unset, bool] = UNSET
    disable_in_files: Union[List[str], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        disable: Union[None, Unset, bool]
        if isinstance(self.disable, Unset):
            disable = UNSET
        else:
            disable = self.disable

        use_copy_buffer: Union[None, Unset, bool]
        if isinstance(self.use_copy_buffer, Unset):
            use_copy_buffer = UNSET
        else:
            use_copy_buffer = self.use_copy_buffer

        use_file_suffix: Union[None, Unset, bool]
        if isinstance(self.use_file_suffix, Unset):
            use_file_suffix = UNSET
        else:
            use_file_suffix = self.use_file_suffix

        max_prompt_tokens: Union[None, Unset, int]
        if isinstance(self.max_prompt_tokens, Unset):
            max_prompt_tokens = UNSET
        else:
            max_prompt_tokens = self.max_prompt_tokens

        debounce_delay: Union[None, Unset, int]
        if isinstance(self.debounce_delay, Unset):
            debounce_delay = UNSET
        else:
            debounce_delay = self.debounce_delay

        max_suffix_percentage: Union[None, Unset, int]
        if isinstance(self.max_suffix_percentage, Unset):
            max_suffix_percentage = UNSET
        else:
            max_suffix_percentage = self.max_suffix_percentage

        prefix_percentage: Union[None, Unset, int]
        if isinstance(self.prefix_percentage, Unset):
            prefix_percentage = UNSET
        else:
            prefix_percentage = self.prefix_percentage

        template: Union[None, Unset, str]
        if isinstance(self.template, Unset):
            template = UNSET
        else:
            template = self.template

        multiline_completions: Union[None, Unset, str]
        if isinstance(self.multiline_completions, Unset):
            multiline_completions = UNSET
        elif isinstance(self.multiline_completions, TabAutocompleteOptionsMultilineCompletionsType0):
            multiline_completions = self.multiline_completions.value
        else:
            multiline_completions = self.multiline_completions

        use_cache: Union[None, Unset, bool]
        if isinstance(self.use_cache, Unset):
            use_cache = UNSET
        else:
            use_cache = self.use_cache

        only_my_code: Union[None, Unset, bool]
        if isinstance(self.only_my_code, Unset):
            only_my_code = UNSET
        else:
            only_my_code = self.only_my_code

        use_other_files: Union[None, Unset, bool]
        if isinstance(self.use_other_files, Unset):
            use_other_files = UNSET
        else:
            use_other_files = self.use_other_files

        disable_in_files: Union[List[str], None, Unset]
        if isinstance(self.disable_in_files, Unset):
            disable_in_files = UNSET
        elif isinstance(self.disable_in_files, list):
            disable_in_files = self.disable_in_files

        else:
            disable_in_files = self.disable_in_files

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if disable is not UNSET:
            field_dict["disable"] = disable
        if use_copy_buffer is not UNSET:
            field_dict["useCopyBuffer"] = use_copy_buffer
        if use_file_suffix is not UNSET:
            field_dict["use_file_suffix"] = use_file_suffix
        if max_prompt_tokens is not UNSET:
            field_dict["maxPromptTokens"] = max_prompt_tokens
        if debounce_delay is not UNSET:
            field_dict["debounceDelay"] = debounce_delay
        if max_suffix_percentage is not UNSET:
            field_dict["maxSuffixPercentage"] = max_suffix_percentage
        if prefix_percentage is not UNSET:
            field_dict["prefixPercentage"] = prefix_percentage
        if template is not UNSET:
            field_dict["template"] = template
        if multiline_completions is not UNSET:
            field_dict["multilineCompletions"] = multiline_completions
        if use_cache is not UNSET:
            field_dict["useCache"] = use_cache
        if only_my_code is not UNSET:
            field_dict["onlyMyCode"] = only_my_code
        if use_other_files is not UNSET:
            field_dict["useOtherFiles"] = use_other_files
        if disable_in_files is not UNSET:
            field_dict["disableInFiles"] = disable_in_files

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_disable(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        disable = _parse_disable(d.pop("disable", UNSET))

        def _parse_use_copy_buffer(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        use_copy_buffer = _parse_use_copy_buffer(d.pop("useCopyBuffer", UNSET))

        def _parse_use_file_suffix(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        use_file_suffix = _parse_use_file_suffix(d.pop("use_file_suffix", UNSET))

        def _parse_max_prompt_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_prompt_tokens = _parse_max_prompt_tokens(d.pop("maxPromptTokens", UNSET))

        def _parse_debounce_delay(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        debounce_delay = _parse_debounce_delay(d.pop("debounceDelay", UNSET))

        def _parse_max_suffix_percentage(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_suffix_percentage = _parse_max_suffix_percentage(d.pop("maxSuffixPercentage", UNSET))

        def _parse_prefix_percentage(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        prefix_percentage = _parse_prefix_percentage(d.pop("prefixPercentage", UNSET))

        def _parse_template(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        template = _parse_template(d.pop("template", UNSET))

        def _parse_multiline_completions(
            data: object,
        ) -> Union[None, TabAutocompleteOptionsMultilineCompletionsType0, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                multiline_completions_type_0 = TabAutocompleteOptionsMultilineCompletionsType0(data)

                return multiline_completions_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, TabAutocompleteOptionsMultilineCompletionsType0, Unset], data)

        multiline_completions = _parse_multiline_completions(d.pop("multilineCompletions", UNSET))

        def _parse_use_cache(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        use_cache = _parse_use_cache(d.pop("useCache", UNSET))

        def _parse_only_my_code(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        only_my_code = _parse_only_my_code(d.pop("onlyMyCode", UNSET))

        def _parse_use_other_files(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        use_other_files = _parse_use_other_files(d.pop("useOtherFiles", UNSET))

        def _parse_disable_in_files(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                disable_in_files_type_0 = cast(List[str], data)

                return disable_in_files_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        disable_in_files = _parse_disable_in_files(d.pop("disableInFiles", UNSET))

        tab_autocomplete_options = cls(
            disable=disable,
            use_copy_buffer=use_copy_buffer,
            use_file_suffix=use_file_suffix,
            max_prompt_tokens=max_prompt_tokens,
            debounce_delay=debounce_delay,
            max_suffix_percentage=max_suffix_percentage,
            prefix_percentage=prefix_percentage,
            template=template,
            multiline_completions=multiline_completions,
            use_cache=use_cache,
            only_my_code=only_my_code,
            use_other_files=use_other_files,
            disable_in_files=disable_in_files,
        )

        tab_autocomplete_options.additional_properties = d
        return tab_autocomplete_options

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
