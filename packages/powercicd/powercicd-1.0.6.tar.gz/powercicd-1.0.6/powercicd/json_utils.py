import copy
import logging
from typing import Any
from jsonpath_ng.ext import parse

log = logging.getLogger(__name__)


def apply_substitution(json_tree, value_path, replacement):
    log.info(f"Applying substitution '{value_path}' -> '{replacement}':")
    parser = parse(value_path)        
    count = 0
    for match in parser.find(json_tree):
        count += 1
        full_path = match.full_path
        value = match.value
        log.info(f"- Replacing at '{full_path}' old value '{value}' with '{replacement}'")
        value.update(json_tree, replacement)
    if count == 0:
        log.info(f"- Substitution '{value_path}' -> '{replacement}' did not match any value.")


def apply_selection_recursively(json_tree:Any, option_object_marker:str, fallback_key:str|None, common_key:str|None, selected_key:str, debug_path=[]):
    """
    Search for key_marker recursively and substitute itself with the value of key_to_use or key_fallback.
    """
    if isinstance(json_tree, dict):
        if option_object_marker in json_tree:
            # Found option_marker { "option_marker": {...} }
            substitutions_by_option = json_tree[option_object_marker]
            
            # verify that the value is a dictionary
            if not isinstance(substitutions_by_option, dict):
                raise ValueError(f"Expected a dictionary value for '{option_object_marker}' at path '{debug_path}'")
            
            result = None
            if common_key is not None and common_key in substitutions_by_option:
                result = copy.copy(substitutions_by_option[common_key])
                # also apply transformations to common values!
                result = apply_selection_recursively(result, option_object_marker, fallback_key, common_key, selected_key, debug_path + [common_key])

            # values to add to common_values                           
            if selected_key in substitutions_by_option:
                log.info(f"At path '{debug_path}' using option '{selected_key}'")
                option_values = substitutions_by_option[selected_key]
            elif fallback_key is not None and fallback_key in substitutions_by_option:
                log.info(f"At path '{debug_path}' using fallback/default option '{fallback_key}'")
                option_values = substitutions_by_option[fallback_key]
            else:
                raise ValueError(f"Neither '{selected_key}' nor '{fallback_key}' found in '{json_tree}' at path '{debug_path}'")
            
            if isinstance(result, dict):
                if not isinstance(option_values, dict):
                    raise ValueError(f"Expected a dictionary value for '{selected_key}' at path '{debug_path}'")
                result.update(option_values)
                return result
            elif isinstance(result, list):
                if not isinstance(option_values, list):
                    raise ValueError(f"Expected a list value for '{selected_key}' at path '{debug_path}'")
                result.extend(option_values)
                return result
            else:
                return option_values
        else:
            return {
                key: apply_selection_recursively(value, option_object_marker, fallback_key, common_key, selected_key, debug_path + [key])
                for key, value 
                in json_tree.items()
            }
    elif isinstance(json_tree, list):
        return [
            apply_selection_recursively(value, option_object_marker, fallback_key, common_key, selected_key, debug_path + [index])
            for index, value in enumerate(json_tree)
        ]
    else:
        return json_tree