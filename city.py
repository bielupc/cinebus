import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
from typing_extensions import TypeAlias
import os
import pickle
from dataclasses import dataclass
from buses import *
from math import radians, sin, cos, sqrt, atan2
import uuid
import threading


###########################
#  Datatypes & constants  #
###########################


CityGraph: TypeAlias = nx.Graph
OsmnxGraph: TypeAlias = nx.MultiDiGraph
Path: TypeAlias = nx.Graph


BUS_LOAD_TIME = 30
BUS_AVERAGE_SPEED = 15
EARTH_RADIUS = 6371
WALKING_AVERAGE_SPEED = 5


@dataclass(frozen=True)
class Cruilla:
    """Dataclass that represents a crossroads node."""
    pos: Coord
    street_count: int


@dataclass(frozen=True)
class Carrer:
    """Dataclass used to represent an edge between crossroads."""
    identifier: int | uuid.UUID
    oneway: bool
    name: str
    street_type: str
    maxspeed: int
    length: float


@dataclass(frozen=True)
class Bus:
    """Dataclass used to represent an edge between stops."""
    line: Line
    length: float
    stop_a: Stop
    stop_b: Stop


####################################
#        Data visualization        #
####################################


def plot(g: CityGraph, nom_fitxer: str) -> None:
    """Creates a file with name nom_fitxer of the provided City Graph g."""
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OSM)
    for edge in g.edges():
        n1 = staticmaps.create_latlng(g.nodes(
            data=True)[edge[0]]["data"].pos[0], g.nodes(data=True)[edge[0]]["data"].pos[1])
        n2 = staticmaps.create_latlng(g.nodes(
            data=True)[edge[1]]["data"].pos[0], g.nodes(data=True)[edge[1]]["data"].pos[1])
        context.add_object(staticmaps.Line(
            [n1, n2], color=staticmaps.BLUE, width=1))
    image = context.render_pillow(1200, 800)
    image.save(nom_fitxer+".png")


def show(g: CityGraph) -> None:
    """Given the City Graph, it gets shown interactively as a matplotlib window."""
    plt.figure(figsize=(8, 6))
    pos = {node[0]: (node[1]["data"].pos) for node in g.nodes(data=True)}

    # Optional configs to change node and edges colors
    node_types = {node[0]: "stop" if isinstance(
        node[1]["data"], Stop) else "cruilla" for node in g.nodes(data=True)}
    color_mapping = {"stop": "red", "cruilla": "blue"}
    node_colors = [color_mapping[node_types[node]] for node in g.nodes]
    edges, colors = zip(*nx.get_edge_attributes(g, 'color').items())

    nx.draw(g, pos=pos, with_labels=False, node_size=50,
            node_color=node_colors, edgelist=edges, edge_color=colors)
    plt.show()


def plot_path(g: CityGraph, p: Path, filename: str) -> None:
    """Given the City Graph and a path, it saves a file with name "filename" of the drawed path onto the city."""
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OSM)
    for edge in p.edges():
        n1 = staticmaps.create_latlng(*p.nodes(data=True)[edge[0]]["pos"])
        n2 = staticmaps.create_latlng(*p.nodes(data=True)[edge[1]]["pos"])
        context.add_object(staticmaps.Line(
            [n1, n2], color=staticmaps.BLUE, width=5))
    image = context.render_pillow(1200, 800)
    image.save(filename+".png")


######################
#      Auxiliary     #
######################


def get_distance(p1: Coord, p2: Coord) -> float:
    """Given two points as coordinates, it returns a float corresponding to their euclidian distance using the Haversine formula."""
    lat1 = radians(p1[0])
    lon1 = radians(p1[1])
    lat2 = radians(p2[0])
    lon2 = radians(p2[1])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS * c * 1000  # Convert to meters


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
    """Performs the action of saving the Osmnx graph at ./data/filename.pickle."""
    if not os.path.exists("data"):
        os.mkdir("data")
    print("----SAVING CITY GRAPH----")
    pickle.dump(g, open(f"data/{filename}.pickle", "wb"))


def load_osmnx_graph(filename: str) -> OsmnxGraph:
    """Performs the action of loading the Osmnx graph at ./data/filename.pickle."""
    try:
        return pickle.load(open(f"data/{filename}.pickle", "rb"))
    except NameError:
        print("File not found, check filename!")


####################################
#   Data adquisition & handeling   #
####################################


def get_osmnx_graph() -> OsmnxGraph:
    """It acquires the Osmnx graph of Barcelona and saves it at the ./data directory. If it's already there, it just gets loaded."""
    if os.path.exists("data/osmnxgraph.pickle"):
        print("----LOADING CITY GRAPH----")
        return pickle.load(open("data/osmnxgraph.pickle", "rb"))

    else:
        print('----DOWNLOADING CITY GRAPH DATA-----')
        g = ox.graph_from_place(
            "Barcelona", network_type="walk", simplify=True)

        # This removes the geometry data attribute which is not needed
        for u, v, key, geom in g.edges(data="geometry", keys=True):
            if geom is not None:
                del (g[u][v][key]["geometry"])

        save_osmnx_graph(g, "osmnxgraph")
        return g


def _build_carrer(carrer: dict) -> Carrer:
    """Given a raw dictionary coming from an Osmnx edge, it scrapes all the needed attributes to build the Carrer object."""
    speed = carrer.get(
        "maxspeed", 30)  # In case of no speed provided, it inputs the mode, which is 30
    # If multiple speeds are provided, it takes the maximum and it's converted from str to int
    if type(speed) == list:
        speed = int(max(speed))
    else:
        speed = int(speed)
    return Carrer(carrer["osmid"], carrer["oneway"], carrer.get("name", "no name"), carrer["highway"], speed, carrer["length"])


def _build_bus(line: dict) -> Bus:
    """Works as a constructor of the dataclass Buss by scraping all the needed values of the dictionary line proviede as a parameter."""
    length = get_distance(line[0].pos, line[1].pos)
    return Bus(line[2]["info"], length, line[0], line[1])


######################
#        Main        #
######################


def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
    """
    Given an Osmnx graph of Barcelona, and a Buses graph of all the bus lines and stops of the ATM, it merges them into a single graph using the asked criteria:

    * Stops from Buses graph connected by Bus edges.
    * Cruilles from Osmnx graph connected by Carrer edges.
    * Each stop is connected through a Carrer to the closest Cruilla.
    """
    G = nx.Graph()

    # It adds all the cruilles from OsmnxGraph
    for cruilla in g1.nodes(data=True):
        G.add_node(cruilla[0], data=Cruilla(
            (cruilla[1]["y"], cruilla[1]["x"]), cruilla[1]["street_count"]))  # Inverted coordinates

    # It adds all the stops from BusGraph
    for stop in g2.nodes(data=True):
        # It filters the data only from Barcelona
        if stop[0].municipality == "Barcelona":
            G.add_node(stop[0].stop_id, data=stop[0])

            # It finds the nearest cruilla to the added Stop
            nearest_node = None
            min_distance = float('inf')
            for node in G.nodes(data=True):
                if type(node[1]["data"]) == Cruilla:
                    distance = get_distance(stop[0].pos, node[1]["data"].pos)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_node = node[0]

            carrer = Carrer(uuid.uuid1(
            ), False, f"{stop[0].stop_id}-{nearest_node}", "walk", WALKING_AVERAGE_SPEED, min_distance)
            G.add_edge(stop[0].stop_id, nearest_node, data=carrer,
                       color="black", weight=min_distance/WALKING_AVERAGE_SPEED)

    # It adds all the edges from the OsmnGraph
    for carrer_data in g1.edges(data=True):
        carrer = _build_carrer(carrer_data[2])
        G.add_edge(carrer_data[0], carrer_data[1], data=carrer,
                   color="blue", weight=carrer.length/carrer.maxspeed)

    # It adds all the bus stops connections from BusGraph.
    for line_data in g2.edges(data=True):
        if line_data[0].municipality == "Barcelona" and line_data[1].municipality == "Barcelona":
            dist = get_distance(line_data[0].pos, line_data[1].pos)
            G.add_edge(line_data[0].stop_id, line_data[1].stop_id, data=_build_bus(
                line_data), color="red", weight=(dist/BUS_AVERAGE_SPEED))  # + BUS_LOAD_TIME)

    # The graph creation takes from 3 to 5 minutes, it's worth dumping the graph onto a pickle file to prevent remaking the long computations.
    pickle.dump(G, open(f"data/citygraph.pickle", "wb"))

    return G


def find_path(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord) -> Path:
    """Given ox_g the graph of the streets of Barcelona and g, a CityGraph with all the information of Bus stops and lines, it provides the fastes path (in time)to go from scr to dst. Either on foot or by bus."""

    # It creates the graph and adds source and destination
    path = nx.Graph()
    path.add_node("src", pos=src)
    path.add_node("dst", pos=dst)

    # It find the nearest actual nodes in the graph, closest to the coordinates provided.
    src_nearest = ox.distance.nearest_nodes(ox_g, src[1], src[0])
    dst_nearest = ox.distance.nearest_nodes(ox_g, dst[1], dst[0])

    route = nx.shortest_path(g, src_nearest, dst_nearest, weight="weight")

    # It adds the nodes of the route
    for node in route:
        path.add_node(node, pos=(g.nodes(data=True)[node]["data"].pos))

    # It connects the nodes
    for i in range(0, len(route)-1):
        path.add_edge(route[i], route[i+1])

    path.add_edge("src", route[0])
    path.add_edge(route[-1], "dst")

    return path