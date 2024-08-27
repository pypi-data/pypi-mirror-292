from typing import List, Sequence, Tuple, Union

import numpy as np
from shapely import affinity
from shapely import geometry as geom
from shapely import make_valid
from shapely.ops import unary_union


def polygon_from_left_top_width_height_coords(coords: Union[Tuple[float, float, float, float], np.ndarray]):
    """Create a LocationAttributeValue for a box in the form [x,y,w,h]

    Args:
        coords: A sequence of box in the form [x,y,w,h]
    """
    x0, y0, w, h = coords
    x1 = x0 + w
    y1 = y0 + h
    _coords = [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]
    return geom.Polygon(_coords)


def try_make_polygon_valid_if_invalid(shape):
    if shape.is_valid:
        return shape

    valid_shape = make_valid(shape)
    if not isinstance(valid_shape, (geom.MultiPolygon, geom.Polygon)):
        raise ValueError(f"Invalid Polygon/MultiPolygon {shape}")
    return valid_shape


def polygon_from_coords(
    coords: Sequence[
        Union[Tuple[float, float], Tuple[float, float, float], np.ndarray, Sequence[geom.Point]]
    ],
    fix_invalid_polygons: bool = False,
):
    """
    Args:
        coords: A sequence of (x, y [,z]) numeric coordinate pairs or triples, or
        an array-like with shape (N, 2) or (N, 3).
        Also can be a sequence of Point objects.
    """
    if len(coords) < 3:
        raise ValueError(f"Polygon must have at least 3 coordinates: {coords}")

    value = geom.Polygon(coords)
    if fix_invalid_polygons:
        value = try_make_polygon_valid_if_invalid(value)
    return value


def polygon_from_tlbr(x: Tuple[int, int, int, int]) -> geom.Polygon:
    """
    from top left bottom right format
    """
    top_left = x[0], x[1]
    top_right = x[2], x[1]
    bottom_right = x[2], x[3]
    bottom_left = x[0], x[3]
    return geom.Polygon(np.array([top_left, top_right, bottom_right, bottom_left]))


def multipolygon_from_coords(
    coords: Sequence[Sequence[Tuple[float, float]]],
    fix_invalid_polygons: bool = False,
):
    """
    Args:
        coords: A nested sequence of (x, y) numeric coordinate pairs, or
        an array-like with shape (N, 2).
    """
    shapes = []
    for poly_xys in coords:
        shape = geom.Polygon(poly_xys)
        if fix_invalid_polygons:
            shape = try_make_polygon_valid_if_invalid(shape)
        shapes.append(shape)

    if len(shapes) == 1:
        value = shapes[0]
    else:
        value = unary_union(shapes)
    return value


def get_top_left_bottom_right_coordinates(
    value: geom.Polygon, scale: float = 1.0, scale_about_origin: bool = True, pad: int = 0
) -> Tuple[int, int, int, int]:
    """
    to top left bottom right format
    """
    bounds: geom.Polygon = geom.box(*value.bounds)

    if scale_about_origin:
        bounds = affinity.scale(bounds, xfact=scale, yfact=scale, origin=(0, 0, 0))
    else:
        bounds = affinity.scale(bounds, xfact=scale, yfact=scale, origin="center")

    bounds = bounds.buffer(pad, join_style="bevel")
    return bounds.bounds
