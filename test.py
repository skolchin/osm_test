import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from itertools import combinations
from collections import OrderedDict

# Load geojson
gdf = gpd.read_file('2927889.json')

# Extract 1st and last point of each feature's geometry
points = {}
features = OrderedDict()
for feature in gdf.iterfeatures():
    id = feature['properties']['id']
    points[id] = (feature['geometry']['coordinates'][0], feature['geometry']['coordinates'][-1])
    features[id] = feature['geometry']

# Calculate distance between points
new_features = OrderedDict()
used_features = {x: False for x in features.keys()}

def merge(a, b):
    c = list(a)
    c.extend(list(b)[1:])
    return tuple(c)

for idx in combinations(points, 2):

    p_a = (Point(points[idx[0]][0]), Point(points[idx[0]][1]))
    p_b = (Point(points[idx[1]][0]), Point(points[idx[1]][1]))

    d = (p_a[0].distance(p_b[0]), p_a[0].distance(p_b[1]),
         p_a[1].distance(p_b[0]), p_a[1].distance(p_b[1]))
    print(idx, d)

    if d[1] == 0.0:
        # append A to the end of B
        print('-> Appending A to B')
        print(used_features[idx[0]], used_features[idx[1]])
        new_features[idx[1]] = features[idx[1]]
        new_features[idx[1]]['coordinates'] = merge(features[idx[1]]['coordinates'], features[idx[0]]['coordinates'])
        new_features[idx[1]]['merge_from'] = idx
        for i in idx:
            used_features[i] = True
    elif d[2] == 0.0:
        # append B to the end of A
        print('-> Appending B to A')
        print(used_features[idx[0]], used_features[idx[1]])
        new_features[idx[0]] = features[idx[0]]
        new_features[idx[0]]['coordinates'] = merge(features[idx[0]]['coordinates'], features[idx[1]]['coordinates'])
        new_features[idx[0]]['merge'] = idx
        for i in idx:
            used_features[i] = True
    elif d[0] == 0.0 or d[3] == 0.0:
        # tbd
        print('-> Vectors overlapped')
    else:
        # Nothing to do
        print('-> Nothing to do')

# Add features not used before
##nonmerged_features = [x for x in used_features.items() if not x]
##if len(nonmerged_features) > 0:
##    print('Some features were not merged')
##    for id in nonmerged_features.keys():
##        new_features[id] = features[id]

print(set(features.keys()).difference(set(new_features.keys())))