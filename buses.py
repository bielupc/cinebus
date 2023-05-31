import networkx as nx
from dataclasses import dataclass
import requests
from requests.exceptions import HTTPError
import json
from typing import TypeAlias
import os
import pickle
import matplotlib.pyplot as plt
import staticmaps


######################
#     Datatypes      #
######################


BusesGraph: TypeAlias = nx.Graph
Coord : TypeAlias = tuple[float, float]   # (latitude, longitude)


@dataclass(frozen=True)
class Line:
    """"Hashable dataclass that holds data for a bus line"""
    identifier: int
    name: str
    company: str
    active: bool


@dataclass(frozen=True)
class Stop:
    """"Hashable dataclass that holds data for a bus stop"""
    pos: Coord
    name: str
    order: int
    line_id: int
    addr: str
    municipality: str
    adapted: bool
    active: bool
    stop_id: int


####################################
#   Data adquisition & handeling   #
####################################


def _get_data() -> dict:
    """
    It retuns a dictionary with all the raw data from bus lines of the ATM.

    Backup:
    It also saves it as a pickle file at ./data/buses_data.pickle so it gets loaded if it already exists, and it's only downloaded when needed.
    """
    if os.path.exists("data/buses_data.pickle"):
        print("----LOADING BUS DATA----")
        return pickle.load(open("data/buses_data.pickle", "rb"))
    else:
        try:
            dataJSON = requests.get(
                "https://www.ambmobilitat.cat/OpenData/ObtenirDadesAMB.json")
            dataJSON.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('----DOWNLOADING BUS DATA-----')

        data = dataJSON.json()
        if not os.path.exists("data"):
            os.mkdir("data")
        pickle.dump(data, open("data/buses_data.pickle", "wb"))
        return data


def _build_stop(data: dict, i: int) -> Stop:
    """Given the dictionary containing the data, it gathers all the needed items regarding a stop, and returns the stop object."""
    return Stop((data["UTM_X"], data["UTM_Y"]), data["Nom"], data["Ordre"], data["IdLinia"], data["Adreca"], data["Municipi"], data["Adaptada"], data["EstatParada"], i)


def _build_line(data: dict) -> Line:
    """Given the dictionary containing the data, it gathers all the needed items regarding a line, and returns the line object."""
    return Line(data["Id"], data["DescripcioInterna"], data["Companyia"], data["Activa"])


####################################
#        Data visualization        #
####################################


def plot(g: BusesGraph, nom_fitxer: str) -> None:
    """Creates a file with name nom_fitxer of the provided bus graph g."""
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OSM)
    for edge in g.edges():
        n1 = staticmaps.create_latlng(edge[0].pos[0], edge[0].pos[1])
        n2 = staticmaps.create_latlng(edge[1].pos[0], edge[1].pos[1])
        context.add_object(staticmaps.Line(
            [n1, n2], color=staticmaps.BLUE, width=1))
    image = context.render_pillow(1200, 800)
    image.save(nom_fitxer)


def show(g: BusesGraph) -> None:
    """Given the bus graph, it gets shown interactively as a matplotlib window."""
    plt.figure(figsize=(8, 6))
    pos = {node: (node.pos[0], node.pos[1]) for node in g.nodes}
    nx.draw(g, pos=pos, with_labels=False, node_size=50, node_color='red')
    plt.show()


######################
#        Main        #
######################


def get_buses_graph() -> BusesGraph:
    """Returns a graph with all the bus lines, stops and their information."""
    G = nx.Graph()
    all_data = _get_data()
    lines_data = all_data["ObtenirDadesAMBResult"]["Linies"]["Linia"]
    previous_stop: Stop

    # Stop ID
    i = 0

    # We iterate over the lines
    for line_data in lines_data:
        line = _build_line(line_data)

        # It skips an iteration if the line is no active
        if not line.active:
            continue

        # It keeps track of the added stops.
        visided_stops: dict[str, Stop] = dict()
        # It iterates over the different stops
        for stop_data in line_data["Parades"]["Parada"]:
            stop = _build_stop(stop_data, i)
            line_id = stop.line_id

            # It skips an iteration if the stop is no active
            if not stop.active:
                continue

            # If it's not the first stop, the node + edge is added.
            if stop.order != 1:
                if not stop.name in visided_stops.keys():
                    G.add_node(stop)
                    i += 1
                    visided_stops[stop.name] = stop
                    G.add_edge(previous_stop, stop, info=line)
                else:
                    # Multiple lines sharing stop scenario.
                    G.add_edge(previous_stop, visided_stops[stop.name],info=line)
            else:
                if not stop.name in visided_stops.keys():
                    G.add_node(stop)
                    i += 1
            # It remembers the last stop we inspected, since the iteration is ordered.
            previous_stop = stop
    return G