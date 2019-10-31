import mplleaflet
from matplotlib import pyplot as plt
import numpy as np
import geopandas
from shapely.geometry import Point, Polygon
import osmnx as ox
from descartes import PolygonPatch
import random
import pandas as pd


def df_to_gdf(df, 
              latitude="latitude", 
              longitude="longitude", 
              crs=None):
    if type(df) is geopandas.GeoDataFrame:
        return df
    
    if crs is None:
        crs = {'init': 'epsg:4326'}
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df[longitude], df[latitude]))
    gdf.crs = crs
    return gdf


def _coordinate_to_id(coordinate, bound, grid_size):
    return int(np.floor(float(coordinate - bound) / grid_size))


def _geometry_to_id(geometry, bounds, grid_size, max_i, max_j):
    idx = _coordinate_to_id(geometry.x, bounds[0], grid_size)
    idy = _coordinate_to_id(geometry.y, bounds[1], grid_size)
    if idx >= 0 and idy >= 0 and idx <= max_i and idy <= max_j:
        return(idx,idy)
    else:
        return np.nan

    
def _add_cell_id(gdf, grid_size, bounds=None):
    if bounds is None:
        maxx = gdf.geometry.dropna().x.max()
        minx = gdf.geometry.dropna().x.min()
        maxy = gdf.geometry.dropna().y.max()
        miny = gdf.geometry.dropna().y.min()
        bounds = Polygon([(minx,miny),(maxx,miny),(maxx,maxy),(minx,maxy),(minx,miny)])
        
    gdf = ox.project_gdf(gdf)
    crs = gdf.crs
    box = ox.project_geometry(bounds)[0]
    bounds = box.bounds

    max_i = _coordinate_to_id(bounds[2], bounds[0], grid_size)
    max_j = _coordinate_to_id(bounds[3], bounds[1], grid_size)

    cell_per_point = []
    gdf["cell_id"] = gdf.geometry.apply(lambda x: _geometry_to_id(x, bounds, grid_size, max_i, max_j))
    return ox.project_geometry(bounds_to_polygon(bounds),crs,to_latlong=True), gdf


def _cell_id_to_polygon(cell_id, bounds, grid_size):
    box = ox.project_geometry(bounds)[0]
    bounds = box.bounds
    i = bounds[0] + (cell_id[0]*grid_size)
    j = bounds[1] + (cell_id[1]*grid_size)
    return Polygon([[i,j],[i+grid_size,j],[i+grid_size,j+grid_size], [i,j+grid_size]])


def bounds_to_polygon(bounds):
    return Polygon([(bounds[0],bounds[1]),
            (bounds[2],bounds[1]),
            (bounds[2],bounds[3]),
            (bounds[0],bounds[3]),
            (bounds[0],bounds[1])])


def add_cell_id(df, grid_size, bounds=None, latitude="latitude", longitude="longitude", crs=None):
    gdf = df_to_gdf(df, latitude, longitude, crs)
    return _add_cell_id(gdf, grid_size, bounds)


def create_grid(df, grid_size, bounds=None, latitude="latitude", longitude="longitude", column=None, crs=None, 
                vmax=10):
    gdf = df_to_gdf(df, latitude, longitude, crs)
    bounds, gdf = _add_cell_id(gdf, grid_size, bounds)
    grid = gdf.groupby("cell_id").count()
    if len(grid) > 0:
        grid["geometry"] = grid.apply(lambda x: _cell_id_to_polygon(x.name, bounds, grid_size),axis=1)
        if column is not None:
            grid["color"] = grid[column].apply(lambda x: min(x,vmax)/vmax * 255)
        grid = ox.project_gdf(geopandas.GeoDataFrame(grid, crs=gdf.crs),to_latlong=True)
    return grid

    
def choropleth(df, grid_size,
               bounds=None, 
               latitude="latitude", 
               longitude="longitude", 
               tiles='cartodb_positron', 
               vmax=10, 
               cmap="viridis", 
               column="latitude", 
               crs=None,
               figsize=None):
    if figsize is None:
        figsize = [10,10] 
    fig = plt.figure(figsize=figsize)
    
    grid = create_grid(df, grid_size, bounds, latitude, longitude, column, crs, vmax)
    
    if len(grid) > 0:
        for idx, r in grid.iterrows():
            color = plt.get_cmap(cmap).colors[int(r.color) if not np.isnan(r.color) else 0]
            plt.gca().add_patch(PolygonPatch(r.geometry, alpha=0.5,color=color, zorder=2))
    return mplleaflet.display(fig, tiles=tiles)