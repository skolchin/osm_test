import os
import numpy as np
import osmnx as ox
import pandas as pd
import geopandas as gpd
import requests
import pyproj
import warnings
import logging
import json

from urllib.parse import quote
from matplotlib import pyplot as plt
from shapely.geometry import Point, Polygon, MultiPolygon, LineString
from itertools import tee
from datetime import datetime

#RELATION_IDS = [347721, 106875, 92399]
#RELATION_IDS = [347721]
RELATION_IDS = [92399]
ROUTE_FILE = 'route-%s.xml'
VIEW_MAP_FILE = 'map-%s.html'
JSON_FILE = 'route-%s.json'
TRACE_FILE = 'trace-%s.json'

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def filter_map(gdf, bbox=[0, 0, 180, 90]):
    p1 = Point(bbox[0], bbox[3])
    p2 = Point(bbox[2], bbox[3])
    p3 = Point(bbox[2], bbox[1])
    p4 = Point(bbox[0], bbox[1])

    np1 = (p1.coords.xy[0][0], p1.coords.xy[1][0])
    np2 = (p2.coords.xy[0][0], p2.coords.xy[1][0])
    np3 = (p3.coords.xy[0][0], p3.coords.xy[1][0])
    np4 = (p4.coords.xy[0][0], p4.coords.xy[1][0])

    filter = gpd.GeoDataFrame(
        gpd.GeoSeries(Polygon([np1, np2, np3, np4])),
        columns=['geometry'],
        crs=gdf.crs)
    return gpd.overlay(gdf, filter, how='intersection')

def calc_dist_ext(d, center):
    """ Finds distance from a center point """
    points_list = []
    for row in d.itertuples():
        if isinstance(row.geometry, Point):
            points_list.append((
                row.Index,
                row.geometry.x,
                row.geometry.y,
                row.geometry.distance(center)))
        elif isinstance(row.geometry, LineString):
            points_list.extend([(
                row.Index,
                p[0],
                p[1],
                Point(p).distance(center)) for p in row.geometry.coords])
        else:
            print('Unknown geom ', row.geometry)

    points_np = np.array(points_list)
    min_pt = points_np[np.argmin(points_np[:, 3])]
    max_pt = points_np[np.argmax(points_np[:, 3])]
    dist = distance.geodesic(min_pt[1:3], max_pt[1:3])

    return points_np, min_pt, max_pt, dist

def random_colors(n):
    """Returns n random colors"""
    from random import randint

    rr = []
    for i in range(n):
        r = randint(0,255) / 255.0
        g = randint(0,255) / 255.0
        b = randint(0,255) / 255.0
        rr.extend([(r,g,b)])
    return rr

##def trace_line(geodesic, s, step):
##    s_dot = []
##    for p in pairwise(s):
##        fwd_azimuth, _, max_dist = geodesic.inv(p[0][0], p[0][1], p[1][0], p[1][1])
##        logging.getLogger(__name__).debug('Tracing from {}:{} to {}:{} by {} -> azimuth = {}, max_dist = {}'.format(
##                p[0][0], p[0][1], p[1][0], p[1][1], step, fwd_azimuth, max_dist))
##        s_dot.append(p[0])
##        cur_p = p[0]
##        while True:
##            next_p = geodesic.fwd(cur_p[0], cur_p[1], fwd_azimuth, step)
##            _, _, dist = geodesic.inv(cur_p[0], cur_p[1], p[1][0], p[1][1])
##            ox.utils.log('Next point is {}:{}, dist from prev point {}:{} is {}'.format(next_p[0], next_p[1], cur_p[0], cur_p[1], dist))
##            if abs(dist) <= step:
##                ox.utils.log('Target point {}:{} reached'.format(p[1][0], p[1][1]))
##                break
##            _, _, dist = geodesic.inv(p[0][0], p[0][1], next_p[0], next_p[1])
##            if abs(dist) > max_dist:
##                ox.utils.log('max dist reached')
##                break
##            s_dot.append(next_p)
##            ox.utils.log('Point {}:{} saved'.format(next_p[0], next_p[1]))
##            cur_p = next_p
##        s_dot.append(p[1])
##    return s_dot

def trace_line(geodesic, s, step):
    s_dot = []
    for p in pairwise(s):
        _, _, max_dist = geodesic.inv(p[0][0], p[0][1], p[1][0], p[1][1])
        np = int(max_dist // step)
        s_dot.append(p[0])
        if np > 0:
            s_dot.extend(geodesic.npts(p[0][0], p[0][1], p[1][0], p[1][1], np))
        s_dot.append(p[1])
    return s_dot

def show_trace(w, ax):
    w.plot(ax=ax)
    p = []
    for r in w.itertuples(index=False):
        p.extend(list(r.geometry.coords))

    p = np.array(p)
    print('Number of points on a trace {}'.format(p.shape[0]))

    ax.scatter(p[:, 0], p[:, 1], color='red', alpha=0.8)

def save_xml(rel_id, W, fn):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    with open(fn, 'w', encoding='utf-8') as f:
        f.write('<osm version="0.6" generator="test">\n')

        idx = 1
        for w in W.itertuples(index=False):
            way_idx = []
            g = w.geometry
            if isinstance(g, Point):
                f.write('<node id="{}" lat="{}" lon="{}" version="1" timestamp="{}" />'.format(
                    idx, g.coords[1], g.coords[0], ts))
                way_idx.append(idx)
                idx += 1
            elif isinstance(g, LineString):
                for c in g.coords:
                    f.write('<node id="{}" lat="{}" lon="{}" version="1" timestamp="{}" />\n'.format(
                        idx, c[1], c[0], ts))
                    way_idx.append(idx)
                    idx += 1
            else:
                raise Exception('Unknown geometry type ' + type(g))

            f.write('<way id="{}" version="1" timestamp="{}">\n'.format(w.osmid, ts))
            for n in way_idx:
                f.write('<nd ref="{}"/>\n'.format(n))

            d = w._asdict()
            for x in ['geometry', 'unique_id', 'osmid', 'nodes', 'element_type']:
                d.pop(x)
            for k, v in d.items():
                if v is not None and v == v:
                    f.write('<tag k="{}" v="{}" />\n'.format(k, v))

            f.write('</way>\n')

        f.write('<relation id="{}" version="1" timestamp="{}">\n'.format(rel_id, ts))
        for w in W.itertuples(index=False):
            f.write('<member type="way" ref="{}" role="forward"/>\n'.format(w.osmid))

        f.write('</relation>\n')
        f.write('</osm>\n')

def get_local_crs(p):
    x = ox.utils_geo.bbox_from_point(p, dist = 500, project_utm = True, return_crs = True)
    return x[-1]

# Base config
ox.utils.config(log_console=False, log_level=logging.DEBUG)

# Start point - Kremlin, Moscow
##gdf_msk = ox.geocode_to_gdf('Moscow, Russia')
##msk_center = gdf_msk.to_crs(rus_crs).iloc[0].geometry.centroid
##with warnings.catch_warnings():
##    warnings.simplefilter("ignore")
##    msk_center = gdf_msk.iloc[0].geometry.centroid
msk_center = Point(37.617734, 55.751999)

# Russia CRS
##rus_crs = pyproj.CRS('EPSG:3576')
rus_crs = get_local_crs(list(msk_center.coords)[0])
geodesic = rus_crs.get_geod()

for r_id in RELATION_IDS:
    route_file = ROUTE_FILE % r_id
    map_file = VIEW_MAP_FILE % r_id

    # Load file from OSM, if not exists
    print('\n==> ID %s' % r_id)
    if not os.path.exists(route_file):
        q = quote('[out:xml]; ( relation(%s); <; ); (._;>;); out meta;' % r_id)
        p = requests.get('http://overpass-api.de/api/interpreter?data=%s' % q)
        if not p.ok:
            print('Error loading relation %s' % r_id)
            break
        else:
            with open(route_file, 'wb') as f:
                f.write(p.content)

    # Load to GDF
    D = ox.geometries.geometries_from_xml(route_file)

    # Extract elements of type 'way' which are roads included into relation
    W = D.loc[D['element_type'] == 'way']
    W = W.drop(columns=W.columns.difference(['osmid','geometry']))

    # Find start/end road points
    # Don't care about how precise this distance is since its only for preliminary estimation
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        W['dist_from_msk'] = W.distance(msk_center)

    # Calculate road length
    term = [W.loc[W['dist_from_msk'].idxmin()], W.loc[W['dist_from_msk'].idxmax()]]
    term_pt = [x.geometry.centroid for x in term]
    p = [np.array(term_pt[0]), np.array(term_pt[1])]
    _, _, dist_1 = geodesic.inv(p[0][0], p[0][1], p[1][0], p[1][1])
    _, _, dist_2 = geodesic.inv(list(msk_center.coords)[0][0], list(msk_center.coords)[0][1], p[1][0], p[1][1])

    print('Road {} length is {:.2f} km, from MSK center is {:.2f} km'.format(r_id, dist_1 / 1000, dist_2 / 1000))

##    dist_1 = term[1].geometry.centroid.distance(term[0].geometry.centroid) / 1000
##    dist_2 = term[1].geometry.centroid.distance(msk_center) / 1000
##    print('Road {} length is {:.2f} km, from MSK center is {:.2f} km'.format(r_id, dist_1, dist_2))

    # Trace road
    # After tracing each geomerty will contain points standing no more than STEP meters from each other
    W_new = W[0:0].drop(columns=['dist_from_msk'])
    STEP = 1000

    for r in W.itertuples(index=False):
        s = list(r.geometry.coords)
        s_new = trace_line(geodesic, s, STEP)

        w = gpd.GeoDataFrame(
            [r.osmid],
            columns=['osmid'],
            geometry=gpd.GeoSeries(
                LineString([Point(p) for p in s_new])),
                crs=W.crs)
        W_new = W_new.append(w, ignore_index=True)

    # Show tracing
    _, (ax1, ax2) = plt.subplots(1, 2)
    show_trace(W, ax1)
    show_trace(W_new, ax2)
    plt.show()

    # Save all to geojson
    #D_dot = D.drop(columns=['nodes'])
    #D_dot.to_file(JSON_FILE % r_id, driver='GeoJSON')
    W_new.to_file(TRACE_FILE % r_id, driver='GeoJSON')

##    # Enrich with tags
##    W_dot = W_new.merge(D.drop(columns=['geometry']), left_on=['osmid'], right_on=['osmid'])
##
##    # Save
##    save_xml(r_id, W_dot, 'test.xml')
##    t = ox.geometries.geometries_from_xml('test.xml')

##    G = ox.graph_from_xml(route_file, simplify=False)

##    term_nodes_idx = [x for x in G.nodes() if G.out_degree(x)==0 and G.in_degree(x)==1]
##    term_nodes = [(G.nodes[x]['y'], G.nodes[x]['x']) for x in term_nodes_idx]
##    print(term_nodes)

##    ox.plot_graph(G, node_color='r', node_edgecolor='k')

##    view_map = ox.plot_graph_folium(G, edge_color='#FF0000', edge_width=1)
##    view_map.save(map_file)

##plt.show()

##map_view = ox.plot_graph_folium(G, edge_width=1, edge_color='#FF0000')
##map_view.save(VIEW_MAP_FILE)

##ax = gdf_start.boundary.plot(color='blue', zorder=2, markersize=0)
##gdf_finish.boundary.plot(ax = ax, color='blue', zorder=2, markersize=0)
##gdf_road.plot(ax=ax, color='red', zorder=3, markersize=0)
####gdf_rus.boundary.plot(color='gray', ax=ax, zorder=1)
##_ = ax.axis('off')
##plt.show()
##

