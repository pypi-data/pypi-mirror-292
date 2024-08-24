import inspect
import math
import os
import pickle

import folium
import geopandas as gpd
import numpy as np
import osmnx as ox
from geopy.distance import geodesic
from urllib.parse import urlencode, urlsplit, urlunsplit

#
# options = {
#    'ox_files_save_path': ox_files_save_path,
#    'network_type': 'drive',
#    'place': 'Costa Rica',
#    'files_prefix': 'costa-rica-',
# }
# Usage example
# handler = PBFHandler(**options)
# handler.load()

import osmnx as ox
import networkx as nx
import pickle
import os


class PBFHandler:
    def __init__(self, **kwargs):
        self.graph = None
        self.nodes = None
        self.edges = None
        self.rebuild = kwargs.pop("rebuild", False)
        self.verbose = kwargs.pop("verbose", False)
        self.place = kwargs.pop('place', 'Costa Rica')
        self.filepath = kwargs.pop('ox_files_save_path', "gis_data/")
        self.file_prefix = kwargs.pop('file_prefix', 'costa-rica-')
        self.network_type = kwargs.pop('network_type', 'all')
        self.graph_file = f"{self.filepath}{self.file_prefix}graph.pkl"
        self.node_file = f"{self.filepath}{self.file_prefix}nodes.pkl"
        self.edge_file = f"{self.filepath}{self.file_prefix}edges.pkl"

    def load(self):
        if self.verbose:
            print("Loading data...")

        files_to_check = [self.graph_file, self.node_file, self.edge_file]

        if self.rebuild:
            for file in files_to_check:
                if os.path.exists(file):
                    os.remove(file)
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath, exist_ok=True)
            # self.process_pbf()
            # self.save_to_pickle()
        if not all(os.path.exists(f) for f in files_to_check):
            self.process_pbf()
            self.save_to_pickle()
        else:
            self.load_from_pickle()

        if self.verbose:
            print("Data loaded successfully.")

    def process_pbf(self):
        """
        Load a PBF file and create a graph.
        """
        try:
            if self.verbose:
                print(f"Processing PBF for {self.place}...")

            self.graph = ox.graph_from_place(self.place, network_type=self.network_type)
            self.nodes, self.edges = ox.graph_to_gdfs(self.graph)

            if self.verbose:
                print("PBF processed successfully.")
        except Exception as e:
            print(f"Error processing PBF: {e}")
            raise

    def save_to_pickle(self):
        """
        Save the graph, nodes, and edges to pickle files.
        """
        try:
            if self.verbose:
                print("Saving data to pickle files...")

            data_to_save = {
                self.graph_file: self.graph,
                self.node_file: self.nodes,
                self.edge_file: self.edges
            }

            for file, data in data_to_save.items():
                if data is not None:
                    with open(file, 'wb') as f:
                        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

            if self.verbose:
                print("Data saved to pickle files successfully.")
        except Exception as e:
            print(f"Error saving to pickle: {e}")
            raise

    def load_from_pickle(self):
        """
        Load the graph, nodes, and edges from pickle files.
        """
        try:
            if self.verbose:
                print("Loading data from pickle files...")

            files_to_load = {
                self.graph_file: 'graph',
                self.node_file: 'nodes',
                self.edge_file: 'edges'
            }

            for file, attr in files_to_load.items():
                with open(file, 'rb') as f:
                    setattr(self, attr, pickle.load(f))

            if self.verbose:
                print("Data loaded from pickle files successfully.")
        except Exception as e:
            print(f"Error loading from pickle: {e}")
            raise

    def plot_graph(self):
        """
        Plot the graph.
        """
        try:
            if self.graph is not None:
                if self.verbose:
                    print("Plotting the graph...")
                ox.plot_graph(self.graph)
                if self.verbose:
                    print("Graph plotted successfully.")
            else:
                print("Graph is not loaded. Please load a PBF file first.")
        except Exception as e:
            print(f"Error plotting the graph: {e}")
            raise


def get_bounding_box_from_points(gps_points, margin=0.001):
    latitudes = [point[0] for point in gps_points]
    longitudes = [point[1] for point in gps_points]

    north = max(latitudes) + margin
    south = min(latitudes) - margin
    east = max(longitudes) + margin
    west = min(longitudes) - margin

    return north, south, east, west


def add_arrows(map_object, locations, color, n_arrows):
    # Get the number of locations
    n = len(locations)

    # If there are more than two points...
    if n > 2:
        # Add arrows along the path
        for i in range(0, n - 1, n // n_arrows):
            # Get the start and end point for this segment
            start, end = locations[i], locations[i + 1]

            # Calculate the direction in which to place the arrow
            rotation = -np.arctan2((end[1] - start[1]), (end[0] - start[0])) * 180 / np.pi

            folium.RegularPolygonMarker(location=end,
                                        fill_color=color,
                                        number_of_sides=2,
                                        radius=6,
                                        rotation=rotation).add_to(map_object)
    return map_object


def extract_subgraph(G, north, south, east, west):
    # Create a bounding box polygon
    # from osmnx v2 this is how it is done
    if ox.__version__ >= '2.0':
        bbox_poly = gpd.GeoSeries([ox.utils_geo.bbox_to_poly(bbox=(west, south, east, north))])
    else:
        bbox_poly = gpd.GeoSeries([ox.utils_geo.bbox_to_poly(north, south, east, west)])

    # Get nodes GeoDataFrame
    nodes_gdf = ox.graph_to_gdfs(G, nodes=True, edges=False)

    # Find nodes within the bounding box
    nodes_within_bbox = nodes_gdf[nodes_gdf.geometry.within(bbox_poly.geometry.unary_union)]

    # Create subgraph
    subgraph = G.subgraph(nodes_within_bbox.index)

    return subgraph


def get_distance_between_points(point_a, point_b, unit='km'):
    if not isinstance(point_a, tuple) or len(point_a) != 2:
        return 0
    if not all(isinstance(x, float) and not math.isnan(x) for x in point_a):
        return 0
    if not isinstance(point_b, tuple) or len(point_b) != 2:
        return 0
    if not all(isinstance(x, float) and not math.isnan(x) for x in point_b):
        return 0
    distance = geodesic(point_a, point_b)
    if unit == 'km':
        return distance.kilometers
    elif unit == 'm':
        return distance.meters
    elif unit == 'mi':
        return distance.miles
    else:
        return 0


tile_options = {
    "OpenStreetMap": "OpenStreetMap",
    "CartoDB": "cartodbpositron",
    "CartoDB Voyager": "cartodbvoyager"
}


def attach_supported_tiles(map_object, default_tile="OpenStreetMap"):
    # Normalize the default tile name to lowercase for comparison
    normalized_default_tile = default_tile.lower()

    # Filter out the default tile layer from the options to avoid duplication
    tile_options_filtered = {k: v for k, v in tile_options.items() if v.lower() != normalized_default_tile}

    for tile, description in tile_options_filtered.items():
        folium.TileLayer(name=tile, tiles=description, show=False).add_to(map_object)


def get_graph(**options):
    handler = PBFHandler(**options)
    handler.load()
    return handler.graph, handler.nodes, handler.edges


def add_query_params(url, params):
    # Parse the original URL
    url_components = urlsplit(url)

    # Parse original query parameters and update with new params
    original_params = dict([tuple(pair.split('=')) for pair in url_components.query.split('&') if pair])
    original_params.update(params)

    # Construct the new query string
    new_query_string = urlencode(original_params)

    # Construct the new URL
    new_url = urlunsplit((
        url_components.scheme,
        url_components.netloc,
        url_components.path,
        new_query_string,
        url_components.fragment
    ))

    return new_url


