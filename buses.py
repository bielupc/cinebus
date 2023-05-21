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

BusesGraph : TypeAlias = nx.Graph

@dataclass
class Line:
  identifier: int
  name: str
  company: str
  active: bool

@dataclass
class Stop:
  x: int
  y: int
  name: str
  order: int
  line_id: int
  addr: str
  municipality: str
  adapted: bool

def _get_data() -> dict:
  """
  It retuns a dictionary with all the raw data from bus lines of the ATM.
  
  Backup:
  It also saves it as a pickle file at ./data/buses_data.pickle so it gets loaded if it already exists, and it's only downloaded when needed.
  """
  if os.path.exists("data/buses_data.pickle"):
    print("----LOADING DATA----")
    return pickle.load(open("data/buses_data.pickle","rb"))
  else:
    try:
      dataJSON = requests.get("https://www.ambmobilitat.cat/OpenData/ObtenirDadesAMB.json")
      dataJSON.raise_for_status()
    except HTTPError as http_err:
      print(f'HTTP error occurred: {http_err}')
    except Exception as err:
      print(f'Other error occurred: {err}')
    else:
      print('----DOWNLOADING DATA-----')

    data = dataJSON.json() 
    if not os.path.exists("data"): os.mkdir("data")
    pickle.dump(data, open("data/buses_data.pickle","wb"))
    return data

def plot(g: BusesGraph, nom_fitxer: str) -> None:
  context = staticmaps.Context()
  context.set_tile_provider(staticmaps.tile_provider_OSM)

  for edge in g.edges():

    n1 = staticmaps.create_latlng(g.nodes[edge[0]]["pos"][0], g.nodes[edge[0]]["pos"][1])
    n2 = staticmaps.create_latlng(g.nodes[edge[1]]["pos"][0], g.nodes[edge[1]]["pos"][1])


    context.add_object(staticmaps.Line([n1, n2], color=staticmaps.BLUE, width=1))

  image = context.render_pillow(1200, 800)
  image.save(nom_fitxer)


def show(g: BusesGraph) -> None:
  """Given the bus graph, it gets shown interactively."""
  pos = nx.get_node_attributes(g, 'pos')
  plt.figure(figsize=(8, 6))
  nx.draw(g, pos, with_labels=False, node_size=50, node_color='skyblue')
  plt.title("Geographical NetworkX Graph")
  plt.show()
  


def _build_stop(data: dict) -> Stop:
  return Stop(data["UTM_X"],data["UTM_Y"],data["Nom"],data["Ordre"],data["IdLinia"],data["Adreca"],data["Municipi"], data["Adaptada"])

def _build_line(data: dict) -> Line:
  return Line(data["Id"], data["DescripcioInterna"], data["Companyia"], data["Activa"])

def _save_graph(g: BusesGraph) -> None:
  if not os.path.exists("data"): os.mkdir("data")
  print('----SAVING GRAPH-----')
  pickle.dump(g, open("data/bus_graph.pickle","wb"))


def get_buses_graph() -> BusesGraph:
  """Returns a graph with all the bus lines, stops and their information."""
  if os.path.exists("data/bus_graph.pickle"):
    print("----LOADING GRAPH----")
    return pickle.load(open("data/bus_graph.pickle","rb"))
  else:
    print('----CREATING GRAPH-----')

    G = nx.Graph()
    all_data = _get_data()
    lines_data =  all_data["ObtenirDadesAMBResult"]["Linies"]["Linia"]

    i=0
    for line_data in lines_data:
      line = _build_line(line_data)
      for stop_data in line_data["Parades"]["Parada"]:
        stop = _build_stop(stop_data)
        if not any(node.name == stop.name for node in nx.get_node_attributes(G, "data").values()):
          G.add_node(i, data=stop, pos=(stop.x, stop.y))
          if G.nodes[i]["data"].order != 1:
            G.add_edge(i-1, i, data=line)
          i+=1
    _save_graph(G)
    return G


G = get_buses_graph() 
plot(G, "graph.png")