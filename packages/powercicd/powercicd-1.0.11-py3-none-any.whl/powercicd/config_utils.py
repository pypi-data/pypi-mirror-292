import fnmatch
from typing import Literal, Tuple, TypeVar, Union


VisibilityAction = Literal["show", "hide", "keep"]


K = TypeVar('K')


def get_first_matching_key_pattern(key_patterns: list[dict[K, str]], txt: str) -> Tuple[K, str] | None:
    for index, key_pattern in enumerate(key_patterns):
        if len(key_pattern) > 1:
            raise ValueError(f"Only one key-pattern pair is allowed in the list, but found {len(key_pattern)} at index {index} in list: {key_patterns}")
        key, pattern = next(iter(key_pattern.items()))
        if fnmatch.fnmatch(txt, pattern):
            return key, pattern
    return None