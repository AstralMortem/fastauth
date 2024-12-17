from typing import Literal, Union, Sequence

TokenType = Literal["access", "refresh"]
StringOrSequence = Union[str, Sequence[str]]
TokenLocations = Literal["headers", "cookies"]
