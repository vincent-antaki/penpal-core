from shapely.geometry import LineString, Polygon
from core.geom import hidden_line_removal, remove_overlapping_polygons

def test_hlr():
    lines = [LineString([(0, 0), (10, 0)])]
    occluders = [Polygon([(4, -1), (6, -1), (6, 1), (4, 1)])]
    visible = hidden_line_removal(lines, occluders)
    assert len(visible) == 2
    assert list(visible[0].coords) == [(0.0, 0.0), (4.0, 0.0)]
    assert list(visible[1].coords) == [(6.0, 0.0), (10.0, 0.0)]

def test_overlapping_polygons():
    polys = [
        Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
        Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
    ]
    fragments = remove_overlapping_polygons(polys)
    assert len(fragments) == 2
    # The bottom poly should be clipped by the top poly
    assert fragments[0].area == 75.0
    assert fragments[1].area == 100.0
