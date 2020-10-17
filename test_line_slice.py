import numpy as np
import pandas as pd
import geopandas as gpd
import pyproj
import contextily as ctx

from matplotlib import pyplot as plt
from shapely.geometry import Point, Polygon, MultiPolygon, LineString
from itertools import tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

s = [
(56.2934911,37.4879662),
(56.2938759,37.4879297),
(56.2938913,37.4882677),
(56.2934528,37.4884390),
(56.2916376,37.4878594),
(56.2925947,37.4877758),
(56.2925624,37.4884850),
(56.2582160,37.5095919),
(56.2583558,37.5093438),
(56.2591495,37.5074111)
]

geodesic = pyproj.Geod(ellps='WGS84')

s_dot = []
STEP = 50
for p in pairwise(s):
    fwd_azimuth, _, max_dist = geodesic.inv(p[0][0], p[0][1], p[1][0], p[1][1])
    s_dot.append(p[0])
    cur_p = p[0]
    while True:
        next_p = geodesic.fwd(cur_p[0], cur_p[1], fwd_azimuth, STEP)
        _, _, dist = geodesic.inv(cur_p[0], cur_p[1], p[1][0], p[1][1])
        if abs(dist) <= STEP:
            print('point 2 reached')
            break
        _, _, dist = geodesic.inv(p[0][0], p[0][1], next_p[0], next_p[1])
        if abs(dist) > max_dist:
            print('max dist reached')
            break
        s_dot.append(next_p)
        cur_p = next_p
    s_dot.append(p[1])

gdf_base = gpd.GeoDataFrame(geometry=gpd.GeoSeries(LineString([Point(p) for p in s])), crs='WGS84')
gdf_pt = gpd.GeoDataFrame(geometry=gpd.GeoSeries([Point(p) for p in s]), crs='WGS84')
gdf_dot = gpd.GeoDataFrame(geometry=gpd.GeoSeries([Point(p) for p in s_dot]), crs='WGS84')

ax = gdf_base.plot(color='blue')
ax.set_aspect('equal')
#ctx.add_basemap(ax=ax, crs='WGS84', zoom=10, source=ctx.providers.OpenTopoMap)

gdf_pt.plot(ax=ax, marker='o', markersize=10, zorder=3, color='green')
gdf_dot.plot(ax=ax, marker='o', markersize=5, zorder=2, color='red')

plt.show()
