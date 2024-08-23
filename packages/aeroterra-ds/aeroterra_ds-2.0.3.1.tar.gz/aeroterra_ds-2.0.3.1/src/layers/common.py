from typing import Optional, List, Union

from arcgis.features import FeatureLayer

import geopandas as gpd

from .constants import ESRI_DATA_TYPES, PYTHON_DATA_TYPES

from exceptions.type_checker import type_checker

@type_checker
def ordinal(n: int):
    """
    Returns the string representing the ordinal of the number n. 
    
    Parameters:
        - n: int wanting to cast to ordinal
    """
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

@type_checker
def get_fields_aux(layer: FeatureLayer):
    """
    Returns a list of the fields of a layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    
    Returns a list of tuples of type (name, alias, field type)
    """
    fields = layer.properties.fields
    condensed_fields = []

    for field in fields:
        name = field.name
        alias = field.alias
        field_type = ESRI_DATA_TYPES.get(field.type, field.type)
        condensed_fields.append((name, alias, field_type))

    return condensed_fields


@type_checker
def field_present_layer(layer: FeatureLayer,
                        field_name: str):
    """
    Checks if field_name is present in layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
        - field_name: Name of the field wanting to check if present.
    
    Returns a bool
    """
    fields = get_fields_aux(layer)
    for field in fields:
        if field[0] == field_name:
            return True
    
    return False


@type_checker
def set_display_field_aux(layer: FeatureLayer,
                          display_field: str):
    """
    Sets the display field to the ask field
    
    Parameters:
        - layer: Layer Item of the structure looking to be modified
        - display_field: Name of the field looking to set as display_field
    """
    if not field_present_layer(layer, display_field):
        raise Exception(f"Field {display_field} Doesn't Exist")

    update_dict = {"displayField": display_field}
    
    return layer.manager.update_definition(update_dict)

@type_checker
def standarize_columns(gdf: gpd.GeoDataFrame):
    new_names = {}
    for column in gdf.columns:
        if column == gdf.geometry.name:
            continue

        new_name = column.lower()
        if new_name[:1].isnumeric():
            new_name = "f"+new_name
        if len(new_name) > 10:
            new_name = new_name[:10]
        new_names[column] = new_name
    
    return gdf.rename(columns=new_names)

@type_checker
def get_display_field_aux(layer: FeatureLayer):
    """
    Returns the display field of a given layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    """
    display_field = layer.properties.displayField

    return display_field

@type_checker
def create_field_dict(name: str,
                      alias: str,
                      data_type: str):
    """
    Given a name, alias and data_type it creates the dictionary of items needed
    for it to be a valid ESRIField Dictionary
    
    Parameters:
        - name: Name of the field looking to be created
        - alias: Alias of the field looking to be created
        - data_type: String representing the data type of the field
            looking to be created
    """
    field = {"nullable": True, "defaultValue": None, "editable": True, "domain": None}
    
    esri_type = PYTHON_DATA_TYPES.get(data_type)
    if esri_type is None and data_type not in ESRI_DATA_TYPES:
        raise Exception(f"{data_type} Is Not A Valid Data Type For ESRI")
    elif esri_type is None:
        esri_type = data_type
    
    field["modelName"] = name
    field["name"] = name
    field["alias"] = alias
    field["type"] = esri_type
    
    if esri_type == "esriFieldTypeString":
        field["length"] = 256
    
    return field


@type_checker
def get_objectid_field_aux(layer: FeatureLayer):
    """
    Returns the name of the field that works as the objectID field
    
    Parameters:
        - layer: Layer Item of the structure looking to be read
    """
    fields = get_fields_aux(layer)
    
    for field in fields:
        if field[2] == "ObjectID":
            return field[0]
    
    raise Exception(f"Couldn't Find ObjectID Field Between Given Fields [{fields}]")


@type_checker
def add_field_aux(layer: FeatureLayer,
                  name: Union[List[str], str],
                  data_type: Union[List[str], str],
                  alias: Optional[Union[List[str], str]] = None):
    """
    Adds a field to the layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be modified
        - name: Name(s) of the field looking to be created
        - data_type: String(s) representing the data type of the field
            looking to be created
        - alias (Optional): Alias(es) of the field looking to be created. If None,
            it'll be the same as name
    """
    if name is isinstance(str):
        name = [name]
    
    if data_type is isinstance(str):
        data_type = [data_type]
    
    if alias is isinstance(str):
        alias = [alias]

    if alias is None:
        alias = name

    if len(name) != len(data_type) or len(data_type) != len(alias):
        raise Exception(f"Name, Data_Types & Alias must be equal Length")

    for new_name in name:
        if field_present_layer(layer, new_name):
            raise Exception(f"Field {new_name} Already Exists")
    
    update_dict = {"fields": []}
    for i, new_name in enumerate(name):
        new_alias = alias[i]
        new_type = data_type[i]
        new_field = create_field_dict(new_name, new_alias, new_type)
        update_dict["fields"].append(new_field)
    
    return layer.manager.add_to_definition(update_dict)

@type_checker
def delete_field_aux(layer: FeatureLayer,
                     name: Union[List[str], str]):
    """
    Deletes a field from the layer
    
    Parameters:
        - layer: Layer Item of the structure looking to be modified
        - name: Name(s) of the field looking to be removed
    """
    if name is isinstance(str):
        name = [name]

    for del_name in name:
        if not field_present_layer(layer, del_name):
            raise Exception(f"Field {del_name} Doesn't Exist")
    
    display_field = get_display_field_aux(layer)
    if display_field in name:
        object_id_field = get_objectid_field_aux(layer)
        set_display_field_aux(layer, object_id_field)

    update_dict = {"fields": []}
    for del_name in name:
        update_dict["fields"].append({"name": name})
    
    return layer.manager.delete_from_definition(update_dict)


