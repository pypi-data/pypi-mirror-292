from typing import Union, Tuple, List

from pyproj import CRS

NUMBER_TYPE = Union[float, int]

CRS_TYPE = Union[str, dict, int, Tuple[str, str], CRS]
BBOX_TYPE = Union[List[NUMBER_TYPE], Tuple[NUMBER_TYPE]]