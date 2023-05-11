from dataclasses import dataclass
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup, Tag
from typing import Iterator 
import json


@dataclass 
class Film: 
    title: str
    genre: str
    director: str
    actors: list[str]
    ...


@dataclass 
class Cinema: 
    name: str
    address: str
    ...


@dataclass 
class Projection: 
    film: Film
    cinema: Cinema
    time: tuple[int, int]   # hora:minut
    language: str
    ...


@dataclass 
class Billboard: 
    films: list[Film]
    cinemas: list[Cinema]
    projections: list[Projection]


def get_addr(soup) -> Iterator[str]:
    for addr in soup.find_all("span", attrs={"class":"lighten"}):
        if len(addr["class"]) == 1:
            yield (addr.text).strip()


def get_cinema(soup) -> Iterator[str]:
    for cinema in soup.find_all("h2", attrs={"class":"tt_18"}):
        yield (cinema.text).strip()


def get_projections(soup) -> Iterator[Tag]:
    for table in soup.find_all("div", attrs={"class":"tabs_box_panels"}):
        yield table.find("div", attrs={"class":"tabs_box_pan item-0"})


def get_film_data(soup) -> tuple[str, str, str, list[str]]:
    dataJSON = soup.find("div", attrs={"class": "j_w"} )
    data= json.loads(dataJSON.attrs["data-movie"])
    return data["title"], data["genre"][0], data["directors"][0], data["actors"]


def read() -> Billboard:
    url = "https://www.sensacine.com/cines/cines-en-72480/"
    for i in range(1, 4):
        try:
            page = requests.get(f"{url}?page={i}")
            page.raise_for_status()
        
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  
        except Exception as err:
            print(f'Other error occurred: {err}')  
        else:
            print('----Success!-----')
        
        soup = BeautifulSoup(page.text, "html.parser")

        cinema_list:  list[Cinema] = list()
        projection_list: list[Projection] = list()
        film_list: list[Film] = list()

        registered: list[str] = list()

        for cinema_name, addr, projections_block in zip(get_cinema(soup), get_addr(soup), get_projections(soup)):
            cinema = Cinema(cinema_name, addr)
            cinema_list.append(cinema)

            for film_data in projections_block.find_all("div", attrs={"class":"item_resa"}):
                title, genre, director, actors = get_film_data(film_data)
                film = Film(title, genre, director, actors)
                
                if title not in registered:
                    registered.append(title)
                    film_list.append(film)

                # sessions
                for projection in film_data.find_all("em"):
                    time = tuple(projection.text.strip().split(":"))

                    projection_list.append(Projection(film, cinema, time, "ESPAÑOL"))
    return Billboard(film_list, cinema_list, projection_list)
     

print(read())