import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
from typing import TypeAlias
import os
import pickle
from dataclasses import dataclass
from buses import *

CityGraph : TypeAlias = nx.Graph
OsmnxGraph : TypeAlias = nx.MultiDiGraph
BusesGraph: TypeAlias = nx.Graph

Coord : TypeAlias = tuple[float, float]   # (latitude, longitude)

BUS_LOAD_TIME = 30


@dataclass(frozen=True)
class Cruilla:
  pos: Coord
  street_count: int


@dataclass(frozen=True)
class Carrer:
  identifier: int
  oneway: bool
  name: str
  street_type: str
  maxspeed: int
  length: float


"""Ja present en el mòdul buses"""
# Parada o stop i bus o line
# @dataclass(frozen=True)
# class Stop:
#     x: int
#     y: int
#     name: str
#     order: int
#     line_id: int
#     addr: str
#     municipality: str
#     adapted: bool
#     active: bool
#     stop_id: int


def show(g: CityGraph) -> None:
    """Given the city graph, it gets shown interactively as a matplotlib window."""
    plt.figure(figsize=(8, 6))
    pos = {node: (node.pos[0], node.pos[1]) for node in g.nodes}
    node_types = {node: "stop" if isinstance(node, Stop) else "cruilla" for node in g.nodes}
    color_mapping = {"stop": "red", "cruilla": "blue"}
    node_colors = [color_mapping[node_types[node]] for node in g.nodes]
    nx.draw(g, pos=pos, with_labels=False, node_size=50, node_color=node_colors)
    plt.show()


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
  if not os.path.exists("data"): os.mkdir("data")
  print("----SAVING CITY GRAPH----")
  pickle.dump(g, open(f"data/{filename}.pickle","wb"))
  
 
def load_osmnx_graph(filename: str) -> OsmnxGraph:
  try:
    return pickle.load(open(f"data/{filename}.pickle","rb"))
  except NameError:
    print("File not found, check filename!")

def get_osmnx_graph() -> OsmnxGraph: 
  if os.path.exists("data/osmnxgraph.pickle"):
    print("----LOADING CITY GRAPH----")
    return pickle.load(open("data/osmnxgraph.pickle","rb"))

  else:
    print('----DOWNLOADING CITY GRAPH DATA-----')
    g = ox.graph_from_place("Barcelona, Catalonia", network_type="drive")
    save_osmnx_graph(g, "osmnxgraph")
    return g

def _build_carrer(carrer: dict) -> Carrer:
  print(Carrer(carrer["osmid"], carrer["oneway"], carrer.get("name", "no name"),carrer["highway"],carrer.get("maxspeed", 30),carrer["length"]))


def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
  G = nx.Graph()

  for stop, cruilla in zip(g2.nodes(data=True), g1.nodes(data=True)):
    G.add_node(stop[0])
    G.add_node(Cruilla((cruilla[1]["y"], cruilla[1]["x"]), cruilla[1]["street_count"])) # Inverted coordinates

  # print(g2.nodes(data=True))

  # for cruilla in g1.nodes(data= True):
    # print(Cruilla((cruilla[1]["x"], cruilla[1]["y"]), cruilla[1]["street_count"]))

  
  # for parada in g2.nodes(data=True):
  #   print(parada[0])

  # for line in g2.edges(data=True):
    # print(line[2]["info"])

  # for carrer in g1.edges(data=True):
  #   carrer = _build_carrer(carrer[2])



  show(G)

g1 = get_osmnx_graph()
g2 = get_buses_graph()
G = build_city_graph(g1, g2)
