import mplleaflet
from matplotlib import pyplot as plt
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import osmnx as ox
from geopy import distance
from geopy import Point as gPoint
from descartes import PolygonPatch
from openpyxl.utils.cell import get_column_letter, column_index_from_string, coordinate_from_string


def to_coordinates(i,j):
    return get_column_letter(i+1) + str(int(j))


def from_coordinates(string):
    i,j = coordinate_from_string(string)
    return column_index_from_string(i)-1,j 


def recover_id(start, cell, cell_size):
    minx, miny, maxx, maxy = cell.bounds
    idx = (minx - start[0]) / cell_size
    idy = (miny - start[1]) / cell_size
    return idx, idy


def get_l(cell):
    minx, miny, maxx, maxy = cell.bounds
    return maxx - minx


def df2geo(df, lat="latitude", lon="longitude", crs=None):
    if crs is None:
        crs = {'init': 'epsg:4326'}
    geo = gpd.GeoDataFrame(df)
    geo["geometry"] = [Point(x[lon], x[lat]) for _, x in geo.iterrows()]
    geo.crs = crs
    return geo


def get_grid_points(points, lat_long_bounds, grid_size=50):
    points = ox.project_gdf(points)
    crs = points.crs
    box = ox.project_geometry(Polygon(lat_long_bounds))[0]
    bounds = box.bounds
    squares = []

    for idi, i in enumerate(range(int(bounds[0]),int(bounds[2]), grid_size)):
        for idj, j in enumerate(range(int(bounds[1]),int(bounds[3]), grid_size)):
            squares.append([to_coordinates(idi,idj),
                            Polygon([[i,j],[i+grid_size,j],[i+grid_size,j+grid_size], [i,j+grid_size]])])

    max_i = idi + 1
    max_j = idj + 1

    grid = [[coord, square] for coord, square in squares]

    indexes = np.array(grid)[:,0].tolist()
    grid_all = MultiPolygon(np.array(grid)[:,1].tolist())
    grid = gpd.GeoDataFrame(grid_all, columns=["geometry"], crs=crs)
    grid["cell_id"] = indexes
    cell_set = set(indexes)

    cell_per_point = []
    for _, row in points.iterrows():
        idx = int(np.ceil(float(row.geometry.x - bounds[0]) / grid_size))
        idy = int(np.ceil(float(row.geometry.y - bounds[1]) / grid_size))
        if idx >= 0 and idy >= 0 and idx <= max_i and idy <= max_j:
            coordinate = to_coordinates(idx,idy)
            if coordinate in cell_set:
                cell_per_point.append(coordinate)
            else:
                cell_per_point.append(np.nan)
        else:
            cell_per_point.append(np.nan)
    points["cell_id"] = cell_per_point
    grid = ox.project_gdf(grid, to_latlong=True)
    return grid, points


def plot_choropleth(grid, points, intersection=None, tiles='cartodb_positron', vmax=10, cmap="viridis", 
                    column="latitude"):
    if intersection is not None:
        grid = gpd.GeoDataFrame([x for x in grid.values if intersection.intersects(x[0])])
    grid.crs = {'init': 'epsg:4326'}
    grid.columns = ["geometry","cell_id"]

    count_cell = points[["cell_id",column]].dropna().groupby("cell_id").count()
    count_cell.columns = ["no"]
    
    aggregated = count_cell.join(grid.set_index("cell_id"))
    aggregated["color"] = aggregated.no.apply(lambda x: min(x,vmax)/vmax * 255)
    
    
    fig = plt.figure(figsize=[10,10])
    for idx, r in aggregated.iterrows():
        color = plt.get_cmap(cmap).colors[int(r.color) if not np.isnan(r.color) else 0]
        plt.gca().add_patch(PolygonPatch(r.geometry, alpha=0.5,color=color, zorder=2))
    return mplleaflet.display(fig, tiles=tiles)


def choropleth(geodf, bounds=None, intersection=None, lat="latitude", lon="longitude", 
               grid_size=50, tiles='cartodb_positron', vmax=10, cmap="viridis", column="latitude"):
    if bounds is None:
        maxx = geodf[lon].dropna().max()
        minx = geodf[lon].dropna().min()
        maxy = geodf[lat].dropna().max()
        miny = geodf[lat].dropna().min()
        bounds = [(minx,miny),(maxx,miny),(maxx,maxy),(minx,maxy),(minx,miny)]
    grid, points = get_grid_points(geodf, bounds, grid_size=grid_size)
    return plot_choropleth(grid, points, intersection=intersection, tiles=tiles, vmax=vmax, cmap=cmap, column=column)