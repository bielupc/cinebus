from dataclasses import dataclass
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup, Tag
from typing import Iterator
import json


######################
#     Datatypes      #
######################


@dataclass
class Film:
    """Dataclass that stores information about a film."""
    title: str
    genre: str
    director: str
    actors: list[str]


@dataclass
class Cinema:
    """Dataclass that stores information about a cinema."""
    name: str
    address: str


@dataclass
class Projection:
    """Dataclass that stores information about a film being projected."""
    film: Film
    cinema: Cinema
    time: tuple[int, int]   # hora:minut
    language: str


@dataclass
class Billboard:
    """Dataclass that holds all the data of the current films on display."""
    films: list[Film]
    cinemas: list[Cinema]
    projections: list[Projection]


####################################
#   Data adquisition & handeling   #
####################################


def _get_film_data(soup: Tag) -> tuple[str, str, str, list[str], str]:
    """
    Given the parsed HTML tag that holds film data, it scrapes all the required attributes for the film dataclass and returns them as a tuple.
    """
    tags = [tag.text.strip()
            for tag in soup.find_all("span", attrs={"class": "bold"})]
    lang = "Dubbed" if "Versión Doblada" in tags else "Original"

    dataJSON = soup.find("div", attrs={"data-movie": True})

    # it makes sure we obtained the right data type for mypy purposes
    if isinstance(dataJSON, Tag):
        data = json.loads(dataJSON.attrs["data-movie"])
        return data["title"], data["genre"][0], data["directors"][0], data["actors"], lang
    else:
        raise AttributeError(
            "Accessing attributes of something is not an HTML tag.")


def _get_addr(soup: BeautifulSoup) -> Iterator[str]:
    """Generator that yields as strings the addreces of all the cinemas given the soup object."""
    for addr in soup.find_all("span", attrs={"class": "lighten"}):
        if len(addr["class"]) == 1:
            yield (addr.text).strip()


def _get_cinema(soup: BeautifulSoup) -> Iterator[str]:
    """
    Generator that yields strings corresponding to the names of the cinemas found on the soup object.
    """
    for cinema in soup.find_all("h2", attrs={"class": "tt_18"}):
        yield (cinema.text).strip()


def _get_projections(soup: BeautifulSoup) -> Iterator[Tag]:
    """
    Generator that yields a parsed HTML (tag) of the different blocks of projections that each cinema offers.
    """
    for table in soup.find_all("div", attrs={"class": "tabs_box_panels"}):
        yield table.find("div", attrs={"class": "tabs_box_pan item-0"})


######################
#        Main        #
######################


def read() -> Billboard:
    """
    It scrapes the Sensacine webpage to return a Billboard object with all the film-related data.
    """
    urls = ["https://www.sensacine.com/cines/cines-en-72480/",
            "https://www.sensacine.com/cines/cines-en-72480/?page=2",
            "https://www.sensacine.com/cines/cines-en-72480/?page=3"]
    billboard = Billboard(list(), list(), list())

    # It iterates over the 3 sub-pages
    for url in urls:
        try:
            page = requests.get(url)
            page.raise_for_status()

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('----Success!-----')

        soup = BeautifulSoup(page.text, "html.parser")

        # It uses generators to get the data ordered by cinema.
        for cinema_name, addr, projections_block in zip(_get_cinema(soup), _get_addr(soup), _get_projections(soup)):
            cinema = Cinema(cinema_name, addr)
            billboard.cinemas.append(cinema)

            # This handles cinemas with no projections.
            try:
                # It gathers the data of each film on the projections block
                for film_data in projections_block.find_all("div", attrs={"class": "item_resa"}):
                    title, genre, director, actors, lang = _get_film_data(
                        film_data)
                    film = Film(title, genre, director, actors)

                    # If the film is not registered yet, it gets added
                    if not any(f.title == title for f in billboard.films):
                        billboard.films.append(film)

                    # It creates an entry for each projection of the film
                    for projection in film_data.find_all("em"):
                        time_parts = projection.text.strip().split(":")
                        time = (int(time_parts[0]), int(time_parts[1]))
                        billboard.projections.append(
                            Projection(film, cinema, time, lang))
            except:
                print("Empty cinema without projections.")

    return billboard