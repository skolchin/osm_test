import pyproj
import osmnx as ox

def get_local_crs(p):  
    x = ox.utils_geo.bbox_from_point(p, dist = 500, project_utm = True, return_crs = True)
    return x[-1]


# Ефремова 18 - Кремль
p1 = (37.569306, 55.722654)
p2 = (37.617734, 55.751999)
dist_expected = 4.49 * 1000

#rus_crs = pyproj.CRS('EPSG:3576')
#geodesic = pyproj.Geod(ellps='WGS84')
rus_crs = get_local_crs(p2)
geodesic = rus_crs.get_geod()

fwd_azimuth, back_azimuth, max_dist = geodesic.inv(p1[0], p1[1], p2[0], p2[1])
print(fwd_azimuth, back_azimuth, dist_expected, max_dist, (max_dist - dist_expected) / max_dist)

# Ефремова 18 - Кацивели
p1 = (37.569306, 55.722654)
p2 = (33.972038, 44.393414)
dist_expected = 1286 * 1000

fwd_azimuth, back_azimuth, max_dist = geodesic.inv(p1[0], p1[1], p2[0], p2[1])
print(fwd_azimuth, back_azimuth, dist_expected, max_dist, (max_dist - dist_expected) / max_dist)

# Ефремова 18 - Петропавловск
p1 = (37.569306, 55.722654)
p2 = (158.643503, 53.024259)
dist_expected = 6802 * 1000

fwd_azimuth, back_azimuth, max_dist = geodesic.inv(p1[0], p1[1], p2[0], p2[1])
print(fwd_azimuth, back_azimuth, dist_expected, max_dist, (max_dist - dist_expected) / max_dist)

