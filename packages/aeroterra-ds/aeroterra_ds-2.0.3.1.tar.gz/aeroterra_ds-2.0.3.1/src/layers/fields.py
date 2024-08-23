from typing import Optional, Dict, List, Union

from .common import get_fields_aux, add_field_aux, set_display_field_aux, delete_field_aux, get_objectid_field_aux
from .gets import get_layer
 
from .layers import read_full_layer_aux, update_layer_aux

from arcgis.gis import GIS
from arcgis.features import FeatureLayer

from exceptions.type_checker import type_checker


@type_checker
def add_field(gis: GIS,
              layer_id: str,
              name: Union[List[str], str],
              data_type: Union[List[str], str],
              alias: Optional[Union[List[str], str]] = None,
              number: Optional[int] = None):
    """
    Adds a field to the layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - name: Name(s) of the field looking to be created
        - data_type: String(s) representing the data type of the field
            looking to be created
        - alias (Optional): Alias(es) of the field looking to be created. If None,
            it'll be the same as name
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)

    return add_field_aux(layer, name, data_type, alias)

@type_checker
def delete_field(gis: GIS,
                 layer_id: str,
                 name: Union[List[str], str],
                 number: Optional[int] = None):
    """
    Deletes a field from the layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - name: Names of the field looking to be removed
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)

    return delete_field_aux(layer, name)

@type_checker
def rename_fields_aux(layer: FeatureLayer,
                      change_names: Dict[str, str]):
    """
    Renames a series of fields from a layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be modified
        - change_names: Dictionary to express the before_name and the new_name. {old: new}
    """
    old_names = []
    data_types = {}
    fields = get_fields_aux(layer)
    for old_name in change_names.keys():
        data_type = None
        for field in fields:
            if field[0] == old_name:
                data_types[old_name] = field[2]
                old_names.append(old_name)
                break
    
    if len(old_names) == 0:
        raise Exception("No Valid Field Found To Change")

    object_id_field = get_objectid_field_aux(layer)

    fields_to_ask = [object_id_field]
    fields_to_ask.extend(old_names)

    old_data = read_full_layer_aux(layer)[fields_to_ask]
    
    new_names = []
    for old_name, new_name in change_names.items():
        data_type = data_types.get(old_name)
        if data_type is None:
            continue
        new_names.append(new_name)
        add_field_aux(layer, new_name, data_type)

    new_data = old_data.rename(columns=change_names)

    adds = update_layer_aux(layer, new_data, columns=new_names)
    for old_name in old_names:
        delete_field_aux(layer, old_name)

    return adds

@type_checker
def rename_fields(gis: GIS,
                  layer_id: str,
                  change_names: Dict[str, str],
                  number: Optional[int] = None):
    """
    Renames a series of fields from a layer
    
    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - change_names: Dictionary to express the before_name and the new_name. {old: new}
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)
    
    return rename_fields_aux(layer, change_names)

@type_checker
def set_display_field(gis: GIS,
                      layer_id: str,
                      display_field: str,
                      number: Optional[int] = None):
    """
    Sets the display field to the ask field

    Parameters:
        - gis: GIS struct from the user that owns the layer
        - layer_id: Layer ID of the layer wanting to be modified
        - display_field: Name of the field looking to set as display_field
        - number (Optional): Layer Number inside the item. If not provided
            it'll be assumed the item should only have 1 layer
    """
    layer = get_layer(gis, layer_id, number)

    return set_display_field_aux(layer, display_field)