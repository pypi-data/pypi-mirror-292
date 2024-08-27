from enum import Enum


class TabAutocompleteOptionsMultilineCompletionsType0(str, Enum):
    ALWAYS = "always"
    AUTO = "auto"
    NEVER = "never"

    def __str__(self) -> str:
        return str(self.value)
