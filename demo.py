import buses as bs
import billboard as bb
import city as ct
from city import Cruilla, Carrer, Bus
import yogi as yg
import os
import pickle
import sys


def clear() -> None:
  os.system("cls||clear")

def user_wait() -> None:
  print()
  input("Press any key to continue...")


class Menu:

  _billboard: bb.Billboard
  _buses: bs.BusesGraph
  _city: ct.CityGraph

  def __init__(self):
    pass

  
  def display(self):
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
    clear()
    print("Algorithmics and Programming II")
    print("Data Science and Engineering, UPC")
    print("Biel Altimira")
    print("Q1 Spring 2023")
    user_wait()
  
  def create_billboard(self) -> None:
    try:
      self._billboard = bb.read()
      print()
      print("Billboard data successfully retrieved and stored!")
      user_wait()

    except LookupError as err:
      print(f"An error has occurred: {err}")
      user_wait()
  
  def show_billboard(self) -> None:
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
    try:
      self._buses= bs.get_buses_graph()
      print()
      print("Bus graph successfully retrieved and stored!")
      user_wait()

    except LookupError as err:
      print(f"An error has occurred: {err}")
      user_wait()
  
  def show_bus_graph(self) -> None:
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
    # For debugging
    self._city= pickle.load(open("data/citygraph.pickle","rb"))
    # try: 

    #   g1 = ct.get_osmnx_graph()

    #   try: 
    #     g2 = self._buses
    #   except:
    #     print("You must first download the Bus graph!")
    #     user_wait()
    #     return

    #   self._city = ct.build_city_graph(g1, g2)
    #   print()
    #   print("City graph successfully retrieved and stored!")
    #   user_wait()
    # except LookupError as err:
    #   print(f"An error has occurred: {err}")
    #   user_wait()

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

  
  def main_choice(self, choice):

    try:
      if choice ==  1:
        self.show_credits()
      elif choice == 2:
        self.create_billboard()
      elif choice == 3:
        self.show_billboard()
      elif choice == 4:
        pass
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
        pass
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
    if choice == 10: sys.exit(1)
    menu.main_choice(choice)



if __name__ == "__main__":
  main()