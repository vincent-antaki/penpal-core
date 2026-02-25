from shapely.geometry import Polygon, LineString, MultiLineString
from typing import List
import shapely

def hidden_line_removal(lines: List[LineString], occluders: List[Polygon]) -> List[LineString]:
    """
    Given a list of lines and a list of occluding polygons,
    removes the segments of lines that fall inside the polygons.
    """
    if not occluders:
        return lines

    union_occluder = shapely.union_all(occluders)

    visible_lines = []
    for line in lines:
        diff = line.difference(union_occluder)
        if diff.is_empty:
            continue
        elif isinstance(diff, LineString):
            visible_lines.append(diff)
        elif isinstance(diff, MultiLineString):
            visible_lines.extend(list(diff.geoms))

    return visible_lines

def remove_overlapping_polygons(polygons: List[Polygon]) -> List[Polygon]:
    """
    Stacks polygons from bottom to top (list order).
    Higher index polygons occlude lower index polygons.
    Returns the visible fragments of the polygons.
    """
    visible_fragments = []
    occluder = Polygon()
    for poly in reversed(polygons):
        if occluder.is_empty:
            visible_fragments.append(poly)
            occluder = poly
        else:
            diff = poly.difference(occluder)
            if not diff.is_empty:
                visible_fragments.append(diff)
            occluder = occluder.union(poly)
    
    return list(reversed(visible_fragments))
