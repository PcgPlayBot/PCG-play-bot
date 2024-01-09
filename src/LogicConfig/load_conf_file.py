from json import load, dump
from os import path

from src.LogicConfig.config_validator import config_validator


def load_conf_file(file_path):
    """Loads conf file from json. Validates it and save changes before returning valid json"""

    if path.exists(file_path):
        file = open(file_path, "r")
        json_content = load(file)
        file.close()

    else:
        new_file = open(file_path, "w")
        new_file.close()
        json_content = {}

    valid_json = validate_json(json_content, config_validator)

    with open(file_path, "w") as json_file:
        dump(valid_json, json_file, indent=4)

    return valid_json


def validate_json(json_content, validator):
    """Calls validator recursively on json"""

    valid_json = dict()

    for key, validator_value in validator.items():

        if "validator" in validator_value:
            valid_json[key] = validate_key_value(
                json_content.get(key), validator_value["default"], validator_value["validator"]
            )
        else:
            valid_json[key] = validate_json(json_content.get(key) or dict(), validator_value)

    return valid_json


def validate_key_value(value, default_value, validator):
    """Validates json content according to validator"""

    expected_type = validator.get("type")

    if expected_type is None:
        return default_value

    if expected_type == "str":
        return validate_str_value(value, default_value, validator)

    elif expected_type == "int":
        return validate_int_value(value, default_value, validator)

    elif expected_type == "bool":
        return validate_bool_value(value, default_value)

    elif expected_type == "str_list":
        return validate_str_list_value(value, default_value, validator)

    else:
        return default_value


def validate_str_value(value, default_value, validator):
    """Validates string attributes"""

    if not isinstance(value, str) or not value:
        return default_value

    accepted_values = validator.get("accepted_values")

    if accepted_values is None or value in accepted_values:
        return value
    else:
        return default_value


def validate_int_value(value, default_value, validator):
    """Validates int attributes"""

    if not isinstance(value, int) or not value:
        return default_value

    accepted_values = validator.get("accepted_values")

    min_value = validator.get("min")
    max_value = validator.get("max")

    if accepted_values is not None and value in accepted_values:
        return value

    elif (min_value is None or value >= min_value) and \
            (max_value is None or value <= max_value):
        return value

    else:
        return default_value


def validate_bool_value(value, default_value):
    """Validates boolean attributes"""

    if not isinstance(value, bool) or value is None:
        return default_value

    else:
        return value


def validate_str_list_value(value, default_value, validator):
    """Validates string list attributes"""

    if not isinstance(value, list) or not value:
        return default_value

    accepted_values = validator.get("accepted_values")

    if accepted_values is None:
        return [item for item in value if isinstance(item, str)]

    else:
        return [item for item in value if item in accepted_values]
