from pydantic import BaseModel
from ctypes import Array, Structure
from typing import Dict, List, Type

from pygfdrivers.avantes.util.param_maps import trig_config_maps


def ctypes_array_to_list(value: Array) -> List[float]:
    if isinstance(value, Array):
        return [value[i] for i in range(len(value))]


def list_to_ctypes_array(value: List[float], array_type: Type[Array]) -> Array:
    if isinstance(value, list):
        return array_type(*value)


def model_to_dict(model: BaseModel, prefix: str = "m_") -> Dict:
    new_dict = {}

    def process_field(model_data: BaseModel, current_prefix: str):
        for field_name, field_info in model_data.model_fields.items():
            field_alias = field_info.alias
            full_field_name = f"{current_prefix}{field_alias}"
            field_value = getattr(model_data, field_name)

            if isinstance(field_value, BaseModel):
                process_field(field_value, f"{full_field_name}_m_")
            else:
                new_dict[full_field_name] = field_value

    process_field(model, prefix)
    return new_dict


def dict_to_model(struct_dict: Dict) -> Dict:
    new_dict = {}

    for key, value in struct_dict.items():
        parts = key.split('m_')
        parts = [part.rstrip('_') for part in parts if part]
        current_dict = new_dict

        for part in parts[:-1]:
            current_dict = current_dict.setdefault(part, {})

        current_dict[parts[-1]] = value

    return new_dict


def ctypes_struct_to_dict(struct: Structure) -> Dict:
    struct_dict = {field[0]: getattr(struct, field[0]) for field in getattr(struct, '_fields_')}
    return struct_dict


def dict_to_ctypes_struct(struct_type: Type[Structure], user_settings: Dict) -> Structure:
    struct = struct_type()
    for key, value in user_settings.items():
        if value:
            try:
                if isinstance(value, bool):
                    set_value = int(value)
                elif isinstance(value, list):
                    array_type = type(getattr(struct, key))
                    set_value = array_type(*value)
                elif isinstance(value, str):
                    if 'Trigger' in key:
                        set_value = trig_config_maps[key.split('_')[-1]][value]
                    else:
                        set_value = value.encode('utf-8')
                else:
                    set_value = value

                setattr(struct, key, set_value)
            except Exception as e:
                raise e
    return struct


def model_to_ctypes_struct(model: BaseModel, struct_type: Type[Structure]) -> Structure:
    model_dict = model_to_dict(model)
    struct_obj = dict_to_ctypes_struct(struct_type, model_dict)
    return struct_obj


def ctypes_struct_to_model(model_class: Type[BaseModel], struct: Structure) -> BaseModel:
    struct_dict = ctypes_struct_to_dict(struct)
    model_dict = dict_to_model(struct_dict)
    model_obj = model_class(**model_dict)
    return model_obj


def compare_structs(struct_1: Structure, struct_2: Structure) -> None:
    diff = 0

    print(f"Comparing {struct_1} and {struct_2} structure...")
    for setting, _ in getattr(struct_1, '_fields_'):
        struct_1_value = getattr(struct_1, setting)
        struct_2_value = getattr(struct_2, setting)

        if isinstance(struct_2_value, Array):
            if len(struct_2_value) > 10:
                struct_1_value = [value for value in struct_1_value[:10]]
                struct_2_value = [value for value in struct_2_value[:10]]
            else:
                struct_1_value = [value for value in struct_1_value]
                struct_2_value = [value for value in struct_2_value]

        if struct_1_value != struct_2_value:
            diff += 1
            print(f"[{setting}] - STRUCT_1: {struct_1_value} || STRUCT_2: {struct_2_value}")

    print(f"Found '({diff})' differences between the configurations.")
