from __future__ import annotations

import html
from abc import abstractmethod

import folium
import geopandas as gpd
import numpy as np
import osmnx as ox
from folium.plugins import Fullscreen


class BaseOsmMap:
    tile_options = {
        "OpenStreetMap": "OpenStreetMap",
        "CartoDB": "cartodbpositron",
        "CartoDB Voyager": "cartodbvoyager"
    }
    # Set default bounds for Costa Rica
    bounds = [[8.0340, -85.9417], [11.2192, -82.5566]]

    def __init__(self, osmnx_graph=None, df=None, **kwargs):
        if osmnx_graph is None:
            raise ValueError('osmnx_graph must be provided')
        if df is None:
            raise ValueError('df must be provided')
        if df.empty:
            raise ValueError('df must not be empty')
        self.df = df.copy()
        self.osmnx_graph = osmnx_graph
        self.lat_col = kwargs.get('lat_col', 'latitude')
        self.lon_col = kwargs.get('lon_col', 'longitude')
        self.osm_map = None
        self.G = None
        self.map_html_title = self._sanitize_html(kwargs.get('map_html_title', 'OSM Basemap'))

        self.zoom_start = kwargs.pop('zoom_start', 13)
        self.fullscreen = kwargs.pop('fullscreen', True)
        self.fullscreen_position = kwargs.pop('fullscreen_position', 'topright')
        self.tiles = kwargs.pop('tiles', 'OpenStreetMap')
        self.verbose = kwargs.pop('verbose', False)
        self.sort_keys = kwargs.pop('sort_keys', None)
        self.dt_field = kwargs.pop('dt_field', None)
        self.dt = None
        self.calc_nearest_nodes = kwargs.pop('calc_nearest_nodes', False)
        self.nearest_nodes = None
        self.max_bounds = kwargs.pop('max_bounds', False)
        self._prepare_df()
        self._initialise_map()


    def _prepare_df(self):
        if self.sort_keys:
            self.df.sort_values(by=self.sort_keys, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.gps_points = self.df[[self.lat_col, self.lon_col]].values.tolist()
        if self.dt_field is not None:
            self.dt = self.df[self.dt_field].tolist()

        if self.calc_nearest_nodes:
            self.nearest_nodes = ox.distance.nearest_nodes(self.osmnx_graph, X=self.df[self.lon_col],
                                                           Y=self.df[self.lat_col])


    def _initialise_map(self):
        gps_array = np.array(self.gps_points)
        mean_latitude = np.mean(gps_array[:, 0])
        mean_longitude = np.mean(gps_array[:, 1])
        self.osm_map = folium.Map(location=[mean_latitude, mean_longitude], zoom_start=self.zoom_start,
                                  tiles=self.tiles, max_bounds=self.max_bounds)
        north, south, east, west = self._get_bounding_box_from_points(margin=0.001)
        self.G = self._extract_subgraph(north, south, east, west)


    def _attach_supported_tiles(self):
        # Normalize the default tile name to lowercase for comparison
        normalized_default_tile = self.tiles.lower()

        # Filter out the default tile layer from the options to avoid duplication
        tile_options_filtered = {k: v for k, v in self.tile_options.items() if v.lower() != normalized_default_tile}

        for tile, description in tile_options_filtered.items():
            folium.TileLayer(name=tile, tiles=description, show=False).add_to(self.osm_map)


    def _get_bounding_box_from_points(self, margin=0.001):
        latitudes = [point[0] for point in self.gps_points]
        longitudes = [point[1] for point in self.gps_points]

        north = max(latitudes) + margin
        south = min(latitudes) - margin
        east = max(longitudes) + margin
        west = min(longitudes) - margin

        return north, south, east, west


    def _extract_subgraph(self, north, south, east, west):
        # Create a bounding box polygon
        # from osmnx v2 this is how it is done
        if ox.__version__ >= '2.0':
            bbox_poly = gpd.GeoSeries([ox.utils_geo.bbox_to_poly(bbox=(west, south, east, north))])
        else:
            bbox_poly = gpd.GeoSeries([ox.utils_geo.bbox_to_poly(north, south, east, west)])

        # Get nodes GeoDataFrame
        nodes_gdf = ox.graph_to_gdfs(self.osmnx_graph, nodes=True, edges=False)

        # Find nodes within the bounding box
        nodes_within_bbox = nodes_gdf[nodes_gdf.geometry.within(bbox_poly.geometry.unary_union)]

        # Create subgraph
        subgraph = self.osmnx_graph.subgraph(nodes_within_bbox.index)

        return subgraph


    @abstractmethod
    def process_map(self):
        # this is to be implemented at the subclass level
        # implement here your specific map logic.
        ...


    def pre_process_map(self):
        # this is to be implemented at the subclass level
        # call super().pre_process_map first to inherit the following behaviour
        ...


    def _post_process_map(self):
        self._attach_supported_tiles()
        self.add_tile_layer()
        self._add_fullscreen()
        self._add_map_title()
        if self.max_bounds:
            self.osm_map.fit_bounds(self.bounds)


    def add_tile_layer(self):
        # Override in subclass and call super().add_tile_layer at the end
        folium.LayerControl().add_to(self.osm_map)


    def _add_fullscreen(self):
        if self.fullscreen:
            Fullscreen(position=self.fullscreen_position).add_to(self.osm_map)


    def _add_map_title(self):
        if self.map_html_title:
            self.osm_map.get_root().html.add_child(folium.Element(self.map_html_title))


    @staticmethod
    def _sanitize_html(input_html):
        return html.escape(input_html)


    def generate_map(self):
        self.pre_process_map()
        self.process_map()
        self._post_process_map()

        return self.osm_map
