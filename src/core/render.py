import drawsvg as draw
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
from dataclasses import dataclass
from typing import Iterable, Union

@dataclass
class Style:
    stroke: str = 'black'
    stroke_width: float = 1.0
    fill: str = 'none'

@dataclass
class StyledGeometry:
    geom: BaseGeometry
    style: Style

@dataclass
class Layer:
    geometries: Iterable
    style: Style

Renderable = Union[BaseGeometry, StyledGeometry, Layer]

def render_svg(items: Iterable[Renderable], width: float, height: float, stroke_width: float = 1, fill: str = 'none', stroke: str = 'black', bg_color: str = 'white') -> draw.Drawing:
    """Renders a list of shapely geometries, StyledGeometries, or Layers to a drawsvg Drawing."""
    d = draw.Drawing(width, height, origin=(0, 0))
    d.append(draw.Rectangle(0, 0, width, height, fill=bg_color))

    default_style = Style(stroke=stroke, stroke_width=stroke_width, fill=fill)

    def add_geom(geom: BaseGeometry, style: Style):
        if geom.is_empty:
            return
        if isinstance(geom, LineString):
            path = draw.Path(stroke=style.stroke, stroke_width=style.stroke_width, fill=style.fill)
            coords = list(geom.coords)
            if not coords: return
            path.M(*coords[0])
            for x, y in coords[1:]:
                path.L(x, y)
            d.append(path)
        elif isinstance(geom, Polygon):
            path = draw.Path(stroke=style.stroke, stroke_width=style.stroke_width, fill=style.fill)
            # Exterior
            ext_coords = list(geom.exterior.coords)
            if not ext_coords: return
            path.M(*ext_coords[0])
            for x, y in ext_coords[1:]:
                path.L(x, y)
            # Interiors
            for interior in geom.interiors:
                int_coords = list(interior.coords)
                if not int_coords: continue
                path.M(*int_coords[0])
                for x, y in int_coords[1:]:
                    path.L(x, y)
            d.append(path)
        elif isinstance(geom, (MultiLineString, MultiPolygon, MultiPoint)):
            for part in geom.geoms:
                add_geom(part, style)
        elif isinstance(geom, Point):
            d.append(draw.Circle(geom.x, geom.y, style.stroke_width/2, fill=style.stroke))

    def process_item(item: Renderable, current_style: Style):
        if isinstance(item, StyledGeometry):
            process_item(item.geom, item.style)
        elif isinstance(item, Layer):
            for sub_item in item.geometries:
                process_item(sub_item, item.style)
        elif isinstance(item, BaseGeometry):
            add_geom(item, current_style)
        elif isinstance(item, (list, tuple)):
            for sub_item in item:
                process_item(sub_item, current_style)

    for item in items:
        process_item(item, default_style)
        
    return d

def save_svg(items: Iterable[Renderable], filepath: str, width: float, height: float, bg_color: str = 'white'):
    """Saves items to the given file path as SVG."""
    d = render_svg(items, width, height, bg_color=bg_color)
    d.save_svg(filepath)
