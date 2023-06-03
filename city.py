import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx00p0
from typing import TypeAlias
import os
import pickle
from dataclasses import dataclass
from buses import *
from math import radians, sin, cos, sqrt, atan2
import uuid
import concurrent.futures

CityGraph : TypeAlias = nx.Graph
OsmnxGraph : TypeAlias = nx.MultiDiGraph
BusesGraph: TypeAlias = nx.Graph

Coord : TypeAlias = tuple[float, float]   # (latitude, longitude)

BUS_LOAD_TIME = 30
BUS_AVERAGE_SPEED = 15
EARTH_RADIUS = 6371


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

@dataclass(frozen=True)
class Bus:
  line: Line
  length: float
  stop_a: Stop
  stop_b: Stop



def get_distance(p1: Coord, p2: Coord) -> float:
    # Convert coordinates from degrees to radians
    lat1 = radians(p1[0])
    lon1 = radians(p1[1])
    lat2 = radians(p2[0])
    lon2 = radians(p2[1])


    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = EARTH_RADIUS * c * 1000  # Convert to meters

    return distance

def plot(g: CityGraph, nom_fitxer: str) -> None:
    """Creates a file with name nom_fitxer of the provided bus graph g."""
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OSM)
    for edge in g.edges():
      n1 = staticmaps.create_latlng(g.nodes(data=True)[edge[0]]["data"].pos[0], g.nodes(data=True)[edge[0]]["data"].pos[1])
      n2 = staticmaps.create_latlng(g.nodes(data=True)[edge[1]]["data"].pos[0], g.nodes(data=True)[edge[1]]["data"].pos[1])
      context.add_object(staticmaps.Line(
          [n1, n2], color=staticmaps.BLUE, width=1))
    image = context.render_pillow(1200, 800)
    image.save(nom_fitxer)

def show(g: CityGraph) -> None:
    """Given the city graph, it gets shown interactively as a matplotlib window."""
    plt.figure(figsize=(8, 6))
    pos = {node[0]: (node[1]["data"].pos) for node in g.nodes(data=True)}

    node_types = {node[0]: "stop" if isinstance(node[1]["data"], Stop) else "cruilla" for node in g.nodes(data=True)}
    color_mapping = {"stop": "red", "cruilla": "blue"}
    node_colors = [color_mapping[node_types[node]] for node in g.nodes]

    edges,colors= zip(*nx.get_edge_attributes(g,'color').items())

    nx.draw(g, pos=pos, with_labels=False, node_size=50, node_color=node_colors, edgelist=edges, edge_color=colors)
    plt.show()

def plot_path(g: CityGraph, p: int, filename: str) -> None: 
  context = staticmaps.Context()
  context.set_tile_provider(staticmaps.tile_provider_OSM)
  # for edge in p.edges():
  #   n1 = staticmaps.create_latlng(*p.nodes(data=True)[edge[0]]["pos"])
  #   n2 = staticmaps.create_latlng(*p.nodes(data=True)[edge[1]]["pos"])
  for i in range(1, len(p)-1):

    # print(g.nodes(data=True)[i]["data"])
    print(p[i])
    n1 = staticmaps.create_latlng(*g.nodes(data=True)[p[i]]["data"].pos)
    n2 = staticmaps.create_latlng(*g.nodes(data=True)[p[i+1]]["data"].pos)

    capital = staticmaps.create_latlng(*g.nodes(data=True)[p[i]]["data"].pos)
    context.add_object(staticmaps.Marker(capital, size=5))
    context.add_object(staticmaps.Line(
        [n1, n2], color=staticmaps.BLUE, width=3))
  image = context.render_pillow(1200, 800)
  image.save(filename)

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
    g = ox.graph_from_place("Barcelona", network_type="walk", simplify=True)

    for u, v, key, geom in g.edges(data = "geometry", keys = True):
      if geom is not None:
          del(graph[u][v][key]["geometry"])

    save_osmnx_graph(g, "osmnxgraph")
    return g

def _build_carrer(carrer: dict) -> Carrer:
  speed = carrer.get("maxspeed", 30)
  if type(speed) == list:
    speed = int(max(speed))
  else:
    speed = int(speed)

  return Carrer(carrer["osmid"], carrer["oneway"], carrer.get("name", "no name"),carrer["highway"],speed,carrer["length"])

def _build_bus(line: dict) -> Bus:
  length = get_distance(line[0].pos, line[1].pos)
  return Bus(line[2]["info"], length, line[0], line[1])


def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
  G = nx.Graph()

  for cruilla in g1.nodes(data=True):
    G.add_node(cruilla[0], data=Cruilla((cruilla[1]["y"], cruilla[1]["x"]), cruilla[1]["street_count"])) # Inverted coordinates


  # threads = []
  
  # for stop in g2.nodes(data=True):
  #   t = threading.Thread(target=stop_management, args=(stop,G, g1, g2))
  #   threads.append(t)
  #   t.start()

  #   # Wait for all threads to finish
  # for t in threads:
  #     t.join()
  # with concurrent.futures.ThreadPoolExecutor() as executor:
  #   executor.map(lambda stop: stop_management(stop, G, g1, g2), g2.nodes(data=True))

  for stop in g2.nodes(data=True):
    if stop[0].municipality == "Barcelona":
      G.add_node(stop[0].stop_id, data=stop[0])

      nearest_node = None
      min_distance = float('inf')
      for node in G.nodes(data=True):
          if type(node[1]["data"]) == Cruilla:
              distance = get_distance(stop[0].pos, node[1]["data"].pos)
              if distance < min_distance:
                  min_distance = distance
                  nearest_node = node[0]
      carrer = Carrer(uuid.uuid1(), False, f"{stop[0].stop_id}-{nearest_node}", "walk", 5, min_distance)
      G.add_edge(stop[0].stop_id, nearest_node,data=carrer, color="black", weigth=min_distance/5)



  for carrer_data in g1.edges(data=True):
    carrer = _build_carrer(carrer_data[2])
    G.add_edge(carrer_data[0], carrer_data[1], data=carrer, color="blue", weigth=carrer.length/carrer.maxspeed)



  for line_data in g2.edges(data=True):
    if line_data[0].municipality == "Barcelona" and line_data[1].municipality == "Barcelona":
      dist = get_distance(line_data[0].pos, line_data[0].pos)
      G.add_edge(line_data[0].stop_id, line_data[1].stop_id, data=_build_bus(line_data), color="red", weigth=(distance/BUS_AVERAGE_SPEED) + BUS_LOAD_TIME)


  pickle.dump(G, open(f"data/citygraph.pickle","wb"))
  show(G)

def find_path(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord) -> None:
  path = nx.Graph()

  path.add_node(1, pos=src)

  src_nearest = ox.distance.nearest_nodes(ox_g, src[1], src[0])
  src_nearest_pos = g.nodes(data=True)[src_nearest]["data"].pos

  dst_nearest = ox.distance.nearest_nodes(ox_g, dst[1], dst[0])
  dst_nearest_pos = g.nodes(data=True)[src_nearest]["data"].pos
  path.add_node(2, pos=dst_nearest_pos)

  path.add_node(2, pos=src_nearest_pos)

  path.add_node(3, pos=dst)

  path.add_edge(1,2)
  path.add_edge(2, 3)

  route = nx.dijkstra_path(g, src_nearest, dst_nearest)

  plot_path(g, route, "path.png")
  print(path)


  # mirar cruilla asignada a parada per tenir camí rectangular
  # per les parades, canviar per cruilla més propera.


g1 = get_osmnx_graph()
g2 = get_buses_graph()
# G = build_city_graph(g1, g2)
G = pickle.load(open("data/citygraph.pickle","rb"))

find_path(g1, G, (41.385555,2.145889),(41.382509, 2.144124))


# plot(G, "grafic2.png")