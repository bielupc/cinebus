import buses as bs
import billboard as bb
import city as ct
from city import Cruilla, Carrer, Bus
import yogi as yg
import os
import pickle
import sys
import time
from geopy.geocoders import Nominatim


def clear() -> None:
    """Clears the console screen."""
    os.system("cls||clear")


def user_wait() -> None:
    """Waits for the user to press any key and continue executing."""
    print()
    input("Press any key to continue...")


class Menu:
    """Class to perform the logistings of the menu of Cinebus."""

    _billboard: bb.Billboard
    _buses: bs.BusesGraph
    _city: ct.CityGraph
    _ox_g: ct.OsmnxGraph

    def display(self):
        """Displays the main menu and options of the application"""
        clear()
        print('''
                88                           88
                ""                           88
                                            88
    ,adPPYba,  88  8b,dPPYba,    ,adPPYba,  88,dPPYba,   88       88  ,adPPYba,
    a8"     ""  88  88P'   `"8a  a8P_____88  88P'    "8a  88       88  I8[    ""
    8b          88  88       88  8PP"""""""  88       d8  88       88   `"Y8ba,
    "8a,   ,aa  88  88       88  "8b,   ,aa  88b,   ,a8"  "8a,   ,a88  aa    ]8I
    `"Ybbd8"'  88  88       88   `"Ybbd8"'  8Y"Ybbd8"'    `"YbbdP'Y8  `"YbbdP"'

      ''')
        print("(1) Show credits")
        print("(2) Create Billboard")
        print("(3) Show Billboard")
        print("(4) Look through the Billboard")
        print("(5) Create Bus graph")
        print("(6) Show Bus graph")
        print("(7) Create City graph")
        print("(8) Show City graph")
        print("(9) Find route")
        print("(10) Exit :(")
        print()

    def show_credits(self) -> None:
        """Shows the credits of the project."""
        clear()
        print("Algorithmics and Programming II")
        print("Data Science and Engineering, UPC")
        print("Biel Altimira")
        print("Q1 Spring 2023")
        user_wait()

    def create_billboard(self) -> None:
        """Creates the billboard object."""
        try:
            self._billboard = bb.read()
            print()
            print("Billboard data successfully retrieved and stored!")
            user_wait()
        except LookupError as err:
            print(f"An error has occurred: {err}")
            user_wait()

    def show_billboard(self) -> None:
        """Shows films and cinemas of the billboard object."""
        try:
            print()
            print("FILMS ON DISPLAY")
            for film in self._billboard.films:
                print(film.title)
            print()
            print("OPEN CINEMAS")
            for cinema in self._billboard.cinemas:
                print(cinema.name)
            user_wait()
        except:
            print("You must first download the Billboard (option 2).")
            user_wait()

    def create_bus_graph(self) -> None:
        """Creates the bus graph."""
        try:
            self._buses = bs.get_buses_graph()
            print()
            print("Bus graph successfully retrieved and stored!")
            user_wait()
        except LookupError as err:
            print(f"An error has occurred: {err}")
            user_wait()

    def show_bus_graph(self) -> None:
        """Allows to show interactively or to save as a file the Buses graph."""
        try:
            while True:
                clear()
                print("(1) Show interactively")
                print("(2) Save as png")
                print("(3) Go back")
                print()
                choice = yg.scan(int)

                if choice == 1:
                    bs.show(self._buses)

                elif choice == 2:
                    print("Enter filename (Ex: buses):")
                    filename = yg.scan(str)
                    assert filename is not None
                    bs.plot(self._buses, filename)
                    print(f"The file '{filename}.png' has been created.")
                    user_wait()

                elif choice == 3:
                    break
                else:
                    print()
                    print("You must enter a valid option!")
                    user_wait()
        except:
            print("You must first download the Bus graph!")
            user_wait()

    def create_city_graph(self) -> None:
        """Creates the city graph (It takes from 3-5 minutes)."""

        # For debugging
        # self._city= pickle.load(open("data/citygraph.pickle","rb"))
        # self._ox_g = pickle.load(open("data/osmnxgraph.pickle", "rb"))

        try:
            self._ox_g = ct.get_osmnx_graph()
            g1 = self._ox_g

            try:
                g2 = self._buses
            except:
                print("You must first download the Bus graph!")
                user_wait()
                return

            self._city = ct.build_city_graph(g1, g2)
            print()
            print("City graph successfully retrieved and stored!")
            user_wait()
        except LookupError as err:
            print(f"An error has occurred: {err}")
            user_wait()

    def show_city_graph(self) -> None:
        try:
            while True:
                clear()
                print("(1) Show interactively")
                print("(2) Save as png")
                print("(3) Go back")
                print()
                choice = yg.scan(int)

                if choice == 1:
                    ct.show(self._city)
                elif choice == 2:
                    print("Enter filename (Ex: city):")
                    filename = yg.scan(str)
                    assert filename is not None
                    ct.plot(self._city, filename)
                    print(f"The file '{filename}.png' has been created.")
                    user_wait()
                elif choice == 3:
                    break
                else:
                    print()
                    print("You must enter a valid option!")
                    user_wait()
        except:
            print("You must first download the City graph!")
            user_wait()

    def search_billboard(self) -> None:
        """Allows to perform different filter & search operations on the billboard to find films, cinemas or projections."""
        while True:
            clear()
            print("(1) Search for a film")
            print("(2) Search for a cinema")
            print("(3) Search for a projections")
            print("(4) Go back")
            print()
            choice = yg.scan(int)

            try:
                self._billboard
            except:
                print("You must first download the Billboard!")
                user_wait()
                return
            if choice == 1:
                print("Enter the film you're looking for:")
                query = yg.scan(str)
                assert query is not None
                matches = bb.film_search(self._billboard, query)
                if len(matches) == 0:
                    print("No results were found :( ")
                else:
                    for film in matches:
                        print(film.title)
                        print(f"   * Genre: {film.genre}")
                        print(f"   * Director: {film.director}")
                        print(
                            "   * Actors: {}".format(", ".join(actor for actor in film.actors)))
                        print()
                user_wait()

            elif choice == 2:
                print("Enter the cinema you're looking for:")
                query = yg.scan(str)
                assert query is not None
                cinemas = bb.cinema_search(self._billboard, query)
                if len(cinemas) == 0:
                    print("No results were found :(")
                else:
                    for cinema in cinemas:
                        print(cinema.name)
                        print(f"   * Address: {cinema.address}")
                        print()
                user_wait()

            elif choice == 3:
                print("Enter the exact name of the film you want to watch:")
                query = input()
                projections = bb.cinemas_by_film(self._billboard, query)
                if len(projections) == 0:
                    print("No results were found :( ")
                else:
                    previous = ""
                    for projection in projections:
                        if projection.cinema.name != previous:
                            previous = projection.cinema.name
                            print()
                            print(projection.cinema.name)
                            print(f"   * Address: {projection.cinema.address}")
                            print("   * Sessions:")
                        print("       {}  {}".format("{:02d}:{:02d}".format(
                            *projection.time), projection.language))
                user_wait()
            elif choice == 4:
                break
            else:
                print()
                print("You must enter a valid option!")
                user_wait()

    def find_route(self):
        """Allows the user to find the best route from its current position to the closest cinema based on a film choice."""

        # Checks for required graphs
        try:
            self._ox_g
            self._city
            self._billboard
        except:
            print("You must first download the City graph and Billboard!")
            user_wait()
            return

        try:
            # Current user position
            clear()
            print("Enter your latitude:")
            x = yg.read(float)
            print("Enter your longitude:")
            y = yg.read(float)
            clear()
            # Desired film to watch
            print("Enter the exact title of the film you want to watch:")
            desired_film = input()

            # Optimal cinema
            destination = self.find_destination(desired_film)
            print(desired_film)

            # Path creation
            print("Give your path a name to save:")
            filename = yg.read(str)

            path = ct.find_path(self._ox_g, self._city, (x, y), destination)
            ct.plot_path(self._city, path, filename)

            print("The route you need to follow has been saved as '{}'".format(filename))
            user_wait()
        except:
            print()
            print("An error has occurred!")
            user_wait()

    def find_destination(self, desired_film: str) -> bs.Coord:
        """Given a film, it finds the closest projection time-based and returns its cinema coordinates."""

        # It first gathers the current time
        current_time = time.localtime()
        hour = current_time.tm_hour
        minute = current_time.tm_min
        time_tuple = (hour, minute)

        candidate: bb.Projection | None = None
        min_diff = float("inf")

        # For each projection matching the film name, it gets the closest to the current time
        for projection in self._billboard.projections:
            if projection.film.title == desired_film:
                film_time = projection.time
                hours_diff = film_time[0] - hour
                minute_diff = film_time[1] - minute
                if hours_diff > 0 or (hours_diff == 0 and minute_diff >= 0):
                    diff = hours_diff * 60 + minute_diff
                    if diff < min_diff:
                        candidate = projection
                        min_diff = diff

        if candidate is not None:
            print("No films being projected at this moment")
            sys.exit(1)

        print("Your session is at: \n {}\n{}\n{} ".format(candidate.cinema.name,
              candidate.cinema.address, "{:02d}:{:02d}".format(*candidate.time)))

        # Based on the cinema address, it gets it's global coordinates
        geolocator = Nominatim(user_agent="cinebus")
        location = geolocator.geocode(candidate.cinema.address)
        print(location.address)
        print(location.latitude)
        return location.latitude, location.longitude

    def main_choice(self, choice):
        """Manages the main menu user choice."""
        try:
            if choice == 1:
                self.show_credits()
            elif choice == 2:
                self.create_billboard()
            elif choice == 3:
                self.show_billboard()
            elif choice == 4:
                self.search_billboard()
            elif choice == 5:
                self.create_bus_graph()
            elif choice == 6:
                self.show_bus_graph()
            elif choice == 7:
                self.create_city_graph()
            elif choice == 8:
                self.show_city_graph()
                pass
            elif choice == 9:
                self.find_route()
            else:
                print("You must enter a valid option!")
                user_wait()
        except:
            print("You must enter a valid option!")
            user_wait()


def main() -> None:
    menu = Menu()
    while True:
        menu.display()
        choice = yg.scan(int)
        if choice == 10:
            sys.exit(1)
        menu.main_choice(choice)


if __name__ == "__main__":
    main()