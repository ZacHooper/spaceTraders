import requests
import pandas as pd
import math
import time
import json
from rich.progress import Progress, track
import logging

URL = "https://api.spacetraders.io/"


logging.basicConfig(format='%(asctime)s - %(thread)d - %(levelname)s - %(message)s', level=logging.INFO)

R  = '\033[31m' # red
G  = '\033[32m' # green
W  = '\033[0m'  # white (normal)

class Ship(object):
  '''
  Ship Object

  Parameters
  ----------
  id : String
  manufacturer : String
  kind : String 
      The class of the ship
  type : String
  location : String
  x : int
  y : int
  speed : int
  plating : int
  weapons : int
  maxCargo : int
  spaceAvailable : int
  cargo : List
  '''
  def __init__(self, token, *initial_data, **kwargs):
      self.token = token
      self.cargo = initial_data[0]['cargo']
      self.location = initial_data[0]['location'] if 'location' in initial_data[0] else "IN-TRANSIT"
      self.x = initial_data[0]['x'] if 'location' in initial_data[0] else None
      self.y = initial_data[0]['y'] if 'location' in initial_data[0] else None
      self.kind = initial_data[0]['class']
      for dictionary in initial_data:
          for key in dictionary:
              setattr(self, key, dictionary[key])
      for key in kwargs:
          setattr(self, key, kwargs[key])

  def as_dict(self):
    return {
      "id": self.id,
      "manufacturer": self.manufacturer,
      "class": self.kind,
      "type": self.type,
      "location": self.location,
      "x": self.x,
      "y": self.y,
      "speed": self.speed,
      "plating": self.plating,
      "weapons": self.weapons,
      "maxCargo": self.maxCargo,
      "spaceAvailable": self.spaceAvailable,
      "cargo": self.cargo
    }
  
  # Get Good to sell
  def get_cargo_to_sell(self):
    '''
    Return a list of all the cargo on the ship execpt for FUEL
    '''
    cargo_not_fuel = lambda x: x['good'] != "FUEL"
    cargo_to_sell=list(filter(cargo_not_fuel,self.cargo))
    return cargo_to_sell

  def get_fuel_level(self):
    '''
    Returns an 'int' of the current FUEL onboard the ship
    '''
    fuel = lambda x: x['good'] == "FUEL"
    cargo_fuel=list(filter(fuel,self.cargo))
    return cargo_fuel[0]['quantity'] if len(cargo_fuel) > 0 else 0

  def update_cargo(self, new_cargo, new_spaceAvailable):
    '''
    Updates the cargo & spaceAvailable attributes of this Ship object.

    Enures that any downstream calls of this object have the correct information. Ensure to use this method after any orders.
    '''
    logging.debug("Updating Cargo & Space Available of ship: {0}. Previous Cargo: {1}. New Cargo: {2}. Previous Space Available: {3}. New Space Available: {4}".format(self.id, self.cargo, new_cargo, self.spaceAvailable, new_spaceAvailable))
    self.cargo = new_cargo
    self.spaceAvailable = new_spaceAvailable
    return True

  def update_location(self, new_x, new_y, new_location):
    logging.debug("Updating location of ship. Previous Location: {0}. Previous X: {1}. Previous Y: {2}. New Location: {3}, New X: {4}, New Y: {5}".\
      format(self.location, self.x, self.y, new_location, new_x, new_y))
    self.location = new_location
    self.x = new_x
    self.y = new_y
    return True

  def calculate_fuel_usage(self, from_loc, distance=None, to_loc=None):
    '''
    NOT A PERFECT RESULT

    Based on the distance provided to a location works out the estimated fuel required to fly there

    USAGE:
    Provide already calculated distance 
    OR
    Provide the x & y coordinates of the destination
    '''
    calc_fuel = lambda d, p: round((d / 4) + 1 + p)

    penalties = {
      "MK-I": 2,
      "MK-II": 3,
      "MK-III": 4
    }

    # Calc distance if not supplied
    if distance is None:
      distance = self.calculate_distance(to_loc.x, to_loc.y)
    
    # Calc the penalty
    penalty = penalties[self.kind] if from_loc.type == "PLANET" else 0
    
    return calc_fuel(distance, penalty)


    
  
  def calculate_distance(self, to_x, to_y):
    return round(math.sqrt(math.pow((to_x - self.x),2) + math.pow((to_y - self.y),2)))

  def get_closest_location(self):
    """
    Returns a tuple containing the clostest location to the ship
    
    [0]: A Location object of the closet location
    [1]: Distance to the location
    """
    locations = Game(self.token).locations
    # Remove the ships current location
    locations.pop(self.location)
    # Remove all locations not in the same system as ship
    locations_filtered = {k:v for k,v in locations.items() if self.location[:2] in k}
    # Calculate the closet location
    closet_location = min(locations_filtered.values(), key=lambda loc: self.calculate_distance(loc.x, loc.y))
    return (closet_location, self.calculate_distance(closet_location.x, closet_location.y))
  
  def __repr__(self):
    return """
      id : {0}
      manufacturer : {1}
      kind : {2}
      type : {3}
      location : {4}
      x : {5}
      y : {6}
      speed : {7}
      plating : {8}
      weapons : {9}
      maxCargo : {10}
      spaceAvailable : {11}
      cargo : {12}
    """.format(self.id, self.manufacturer, "temp class", self.type, self.location, self.x, self.y, self.speed, self.plating, self.weapons, self.maxCargo, self.spaceAvailable, self.cargo)
  def __str__(self):
    return """
      id : {0}
      manufacturer : {1}
      kind : {2}
      type : {3}
      location : {4}
      x : {5}
      y : {6}
      speed : {7}
      plating : {8}
      weapons : {9}
      maxCargo : {10}
      spaceAvailable : {11}
      cargo : {12}
    """.format(self.id, self.manufacturer, "temp class", self.type, self.location, self.x, self.y, self.speed, self.plating, self.weapons, self.maxCargo, self.spaceAvailable, self.cargo)

class User:
  '''User Object
  
  https://api.spacetraders.io/#api-users'''
  def __init__(self, token, *args, **kwargs):
    # Handle if Token was incorrectly placed
    if isinstance(token, str):
      self.token = token
    else:
      raise TypeError("Incorrect data type for token")
    # Set user Params from the arguments if user dict provided
    if len(args) == 1:
      self.username = args[0]['username']
      self.credits = args[0]['credits']
      self.ships = self.get_ships(ships=args[0]['ships'])
      self.loans = args[0]['loans']
    # set user params if key word labels used
    else:
      for key in kwargs:
          setattr(self, key, kwargs[key])
  
  def __repr__(self):
    return f"<User Object> "\
           f"Username: {self.username}, "\
           f"Credits: {self.credits}, "\
           f"Ships: {len(self.ships)}, "\
           f"Loans: {len(self.loans)}"

  def request_loan(self, type):
    '''
    API CALL: https://api.spacetraders.io/#api-loans-NewLoan
    '''
    # TODO: Return a loan object
    return generic_post_call("users/{0}/loans".format(self.username), params={"type": type}, token=self.token)

  def buy_ship(self, location, type):
    '''
    API CALL: https://api.spacetraders.io/#api-ships-NewShip
    '''
    # TODO: return a ship object
    # Update the 'ships' attribute of the user
    return generic_post_call("users/{0}/ships".format(self.username), 
                             params={"location": location, "type": type},
                             token=self.token)
  
  def get_ships(self, ships=None, as_df=False, fields=None, sort_by=None, filter_by=None):
    '''
    Returns a list of Ship objects that the user currently owns
    '''
    # Check if the list of ships contains original json data or Ship objects
    # If JSON convert into Ship objects and return
    if ships is not None:
      return [Ship(self.token, ship) for ship in ships]

    return_ships = self.ships
    if filter_by is not None:
      for f in filter_by:
        return_ships = list(filter((lambda x: getattr(x, f[0]) == f[1]), return_ships))
    if sort_by is not None:
      return_ships.sort(key = lambda x: tuple(getattr(x, s) for s in sort_by))
    if as_df:
      return_ships = pd.DataFrame([ship.as_dict() for ship in return_ships])
      if fields is not None:
        return_ships = return_ships.loc[:,fields]

    return return_ships
  
  def get_ship(self, shipId):
    '''
    Returns a Ship object for the shipId provided. 
    
    :Param shipId : str
    :Return ship : Ship 
    '''
    return next((ship for ship in self.ships if ship.id == shipId), None)

  def new_order(self, shipId, good, quantity):
    '''Makes a request to the API to make a buy order. User needs to have suffient funds and can only purchase a maximum of 300 goods at once.
    
    API CALL: https://api.spacetraders.io/#api-purchase_orders-NewPurchaseOrder
    
    Parameters
    ----------
    username : str 
        Username of the user making the buy order
    shipId : str 
        The id of the ship to load the goods onto
    good : str 
        The symbol of the good you want to purchase
    quantity : int 
        The quantity units of the good to buy (Max 300)

    Returns
    -------
    json : a json object
      - credits : contains the user's remaining credits
      - order : contains a json object with details about the buy order
      - ship : contains an updated ship json object with the new goods updated in the cargo

    Errors
    ------
    Status Code : 400
        Error Code : 2003 : Quantity exceeds available cargo space on ship.
    Status Code : 422
        Error Code : 42201 : The payload was invalid. 
            - Ensure all parameters are present and valid.
            - Ensure quantity isn't greater than 300
    '''
    # Prepare for call
    endpoint = "users/{0}/purchase-orders".format(self.username)
    params = {"shipId": shipId, 
              "good": good,
              "quantity": quantity}
    # Make call
    order = generic_post_call(endpoint, params=params, token=self.token)
    # Log the result
    logging.info("Buying {0} units of {1} for {2} at {3}. Remaining credits: {4}. Loading Goods onto ship: {5}"\
      .format(order['order']['quantity'], order['order']['good'], 
              order['order']['total'], order['ship']['location'],
              order['credits'], shipId))
    return order

  def sell_order(self, shipId, good, quantity):
    """Makes a request to the API to sell the goods specifed from the ship specified.

    API CALL: https://api.spacetraders.io/#api-sell_orders-NewSellOrder

    Args:
        shipId ([str]): [id of the ship to sell the goods from]
        good ([str]): [the symbol of the good to sell]
        quantity ([int]): [how many units of the good to sell (Max 300)]

    Returns:
        [json]: [Returns a JSON object containing the user's new credits, the sell order details & the updated ship as a json object]
    """    
    # Prepare for call
    endpoint = "users/{0}/sell-orders".format(self.username)
    params = {
      "shipId": shipId,
      "good": good,
      "quantity": quantity
    }
    # Make call
    order = generic_post_call(endpoint, params=params, token=self.token)
    # Log the result
    logging.info("Selling {0} units of {1} for {2} at {3}. Remaining credits: {4}. Offloading Goods from ship: {5}"\
      .format(order['order']['quantity'], order['order']['good'], 
              order['order']['total'], order['ship']['location'],
              order['credits'], shipId))
    return order

  def fly(self, shipId, destination, track=False):
    endpoint = "users/{0}/flight-plans".format(self.username)
    flight = generic_post_call(endpoint, params={"shipId": shipId,
                                                   "destination": destination}, token=self.token)['flightPlan']
    logging.info("Ship {0} has left {1} and is flying to {2}. It will take {3} seconds.".format(shipId, flight['departure'], destination, flight['timeRemainingInSeconds']))
    # Track the flights progress in the console
    if track:
      # Create Progress Bar
      with Progress() as progress:
        flightTime = flight['timeRemainingInSeconds']
        flight_progress = progress.add_task("[red]Launching...", total=flightTime)

        # Progress updates every second to match the Space Traders API
        for n in range(flightTime):
            progress.update(flight_progress, advance=1)
            if n == 10:
              progress.update(flight_progress, description="[red]In Transit...")
            if n == flightTime-10:
              progress.update(flight_progress, description="[red]Landing...")
            time.sleep(1)
        logging.info("Ship {0} has landed at {1}".format(shipId, destination))
        return flight
    # Don't wont the visual timer in the console
    else:
      # Wait for the length of the flight
      time.sleep(flight['timeRemainingInSeconds'] + 15)
      logging.info("Ship {0} has landed at {1}".format(shipId, destination))
      return flight

  def flight(self, flightPlanId):
    return generic_get_call("users/{0}/flight-plans/{1}".format(self.username, flightPlanId), token=self.token)

class Loan:
  def __init__(self, id, due, repaymentAmount, status, type):
    self.id = id
    self.due = due
    self.repaymentAmount = repaymentAmount
    self.status = status
    self.type = type
  
class Market:
  def __init__(self, game):
    self.game = game

  # Expect DataFrames to be passed to it
  def market_compare(self, from_market, to_market):
    """Returns a DataFrame with matching Goods and the profit made/lost if sold from the 'from_market' to the 'to_market'"""
    # Convert to DataFrames if String value of Symbol provided
    if isinstance(from_market, str):
      from_market = pd.DataFrame(self.game.location(from_market).marketplace())
    if isinstance(to_market, str):
      to_market = pd.DataFrame(self.game.location(to_market).marketplace())
    # Do an Inner Join of the Markets on available goods (symbols)
    market_compare = from_market.join(to_market.set_index('symbol'), on="symbol", how="inner", lsuffix="_from", rsuffix="_to")
    # Get the Profit Margins - factoring in volume of the good
    profit_margin = lambda x: x.sellPricePerUnit_to - x.purchasePricePerUnit_from
    profit_margin_per_volume = lambda x: profit_margin(x) / x.volumePerUnit_from
    market_compare['profit'] = market_compare.apply(profit_margin, axis=1)
    market_compare['profit_per_volume'] = market_compare.apply(profit_margin_per_volume, axis=1)
    return market_compare
  
  def best_buy(self, from_market, to_market):
    """Returns a JSON object with the best Good to buy at the 'from_destination' if wanting to sell goods at the 'to_destination'"""
    # Convert to Location and get market if String value of Symbol provided
    if isinstance(from_market, str):
      from_market = pd.DataFrame(self.game.location(from_market).marketplace())
    if isinstance(to_market, str):
      to_market = pd.DataFrame(self.game.location(to_market).marketplace())
    # Get the market comparison
    market_comparison = self.market_compare(from_market, to_market)
    # Get the record for the best good - factor in the profit per unit volume
    best_good = market_comparison.loc[market_comparison['profit_per_volume'].idxmax()]
    return {"symbol": best_good['symbol'], 
            "cost": best_good['purchasePricePerUnit_from'],  
            "volume": best_good['volumePerUnit_from'],
            "profit": best_good['profit'],
            "profit_per_volume": best_good['profit_per_volume']}

  # Returns the best good to buy, how many units to buy of it and the expected profit
  def what_should_I_buy(self, ship, destination, ship_marketplace=None):
    """
    Returns a JSON object with the best good to buy and how many units of it for a particular ship when travelling to a particular destination
    
    :param ship : Ship - a Ship class object
    :param destination : str - the symbol of the destination to travel too
    :return JSON : best buy
        {
          "symbol": The symbol of the good, 
          "units": How many units you should buy for this ship, 
          "cost": Cost per unit for good
          "total_cost": Total cost of this order, 
          "expected_profit": Expected profit from this order,
          "profit": Profit selling good per unit at destination,
          "profit_per_volume": Profit per volume of selling good at destination, 
          "good_volume": Volume of the good,
          "total_volume": Amount of volume unit will take on the ship,
          "fuel_required": The fuel required to make the trip
        }
    """
    loc = self.game.locations[destination]
    # Get the best good to buy
    if ship_marketplace is None:
      logging.debug("Getting the best goods to trade for from {0} to {1} - Ships Marketplace not supplied".format(ship.location, loc.symbol))
      best_good = self.best_buy(ship.location, loc.symbol)
    else:
      logging.debug("Getting the best goods to trade for from {0} to {1} - Ships Marketplace supplied".format(ship.location, loc.symbol))
      best_good = self.best_buy(pd.DataFrame(ship_marketplace), loc.symbol)
    # How much fuel would be required
    fuel_required = ship.calculate_fuel_usage(self.game.locations[ship.location], to_loc=loc)
    logging.debug("Estimated fuel required from {0} to {1} is: {2}".format(ship.location, loc.symbol, fuel_required))
    # Work out many units to buy
    units_to_buy = math.trunc((ship.maxCargo - fuel_required) / best_good['volume'])
    logging.debug("Given fuel requirement of: {0}, max cargo of: {1}, good volume of: {2}, {3} units should be purchased.".format(fuel_required, ship.maxCargo, best_good['volume'], units_to_buy))
    trade_details = {"symbol": best_good['symbol'], 
                     "units": units_to_buy, 
                     "cost": best_good['cost'],
                     "total_cost": best_good['cost'] * units_to_buy, 
                     "expected_profit": best_good['profit'] * units_to_buy,
                     "profit": best_good['profit'],
                     "profit_per_volume": best_good['profit_per_volume'], 
                     "good_volume": best_good['volume'],
                     "total_volume": best_good['volume'] * units_to_buy,
                     "fuel_required": fuel_required,
                     "from": ship.location,
                     "to": loc.symbol}
    logging.debug("Best good to buy when trading from {} to {} is {}. Trade Details: {}".format(ship.location, loc.symbol, trade_details['symbol'], trade_details))
    return trade_details

class Game:
  """A Game holds constants about the game

  You can save a call to API by initialising a Game object with the systems.json constant
  """    
  def __init__(self, token, systems=None):
    self.token = token
    self.systems = self.load_sytems() if systems is None else systems
    self.locations = self.load_locations()

  def __repr__(self):
    return f"<Game Object> "\
           f"Token: {self.token}, "\
           f"Game Status: {self.status()['status']}"
  
  # See if the game is currently up
  def status(self):
    """Returns whether the game is Up or Not"""
    return generic_get_call("game/status", token=self.token)

  # Get a specific location - returns a location object
  def location(self, symbol):
    """Returns a Location object for the symbol provided"""
    return self.locations[symbol]

  def get_available_ships(self, kind=None):
    """
    Get all the available ships for sale
    
    :param : kind : str - Filter the list of ships to the class of ship provided eg. "MK-I"
    :return : list - List of ships available for purchase

    **CALL TO API**
    """
    return generic_get_call("game/ships", params={"class":kind}, token=self.token)['ships']
  
  def load_sytems(self):
    '''
    This will simply load the complete JSON file with no further transformations
    '''
    # Path handling to account for non relative path usage
    return generic_get_call("game/systems", token=self.token)['systems']
  
  def load_locations(self):
    '''
    This will return a dict of Location objects for all the locations across both systems. The key is the locations symbol.
    '''
    # Return each location as an object with it's symbol as the key
    return {loc['symbol']: Location(self.token, loc) for sys in self.systems for loc in sys['locations']}


class Location:
  def __init__(self, token, *args, **kwargs):
      if isinstance(token, str):
        self.token = token
      else:
        raise TypeError("Incorrect data type for token")
      if len(args) == 1:
        self.symbol = args[0]['symbol']
        self.type = args[0]['type']
        self.name = args[0]['name']
        self.x = args[0]['x']
        self.y = args[0]['y']
        self.allowsConstruction = args[0]['allowsConstruction']
        self.ships = args[0]['ships']
        self.structures = args[0]['structures']
      if len(args) > 1:
        for key in kwargs:
          setattr(self, key, kwargs[key])
  
  def marketplace(self):
    endpoint = "game/locations/{0}/marketplace".format(self.symbol)
    return generic_get_call(endpoint, token=self.token)['location']['marketplace']
  
  def __repr__(self):
    return f"<Location Object> Symbol: {self.symbol}, Type: {self.type}, "\
           f"Name: {self.name}, X: {self.x}, Y: {self.y}, "\
           f"Allows Construction: {self.allowsConstruction}, "\
           f"Ships: {len(self.ships)}, Structures: {len(self.structures)}"

  def __str__(self):
    return "Symbol: " + self.symbol + ", Name: " + self.name

# Get New User 
def post_create_user(username):
  endpoint = "users/{0}/".format(username)
  return generic_post_call(endpoint, params=None)

# Misc Functions
# Generic get call to API
def generic_get_call(endpoint, params=None, token=None):
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get(URL + endpoint, headers=headers, params=params)
    if r.ok:
        return r.json()
    else:
        error = r.json()
        code = error['error']['code']
        message = error['error']['message']
        logging.warning(f"Something went wrong when hitting: {r.request.method} {r.url} with parameters: {params}, Error: {str(error)}")     
        if str(code) == '42901':
          # Handle Throttling errors by pausing and trying again
          logging.warning("Throttle limit was reached. Pausing to wait for throttle")
          time.sleep(10)
          # for n in track(range(10), description="Pausing..."):
          #   time.sleep(1)
          return generic_get_call(endpoint, params, token)
        else:
          logging.exception(f"Something broke the script. Code: {code} Error Message: {message} ")

# Generic call to API
def generic_post_call(endpoint, params=None, token=None):
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.post(URL + endpoint, headers=headers, params=params)
    if r.ok:
        return r.json()
    else:
        error = r.json()
        code = error['error']['code']
        message = error['error']['message']
        logging.warning(f"Something went wrong when hitting: {r.request.method} {r.url} with parameters: {params}, Error: {str(error)}")
        if str(code) == '42901':
          # Handle Throttling errors by pausing and trying again
          logging.warning("Throttle limit was reached. Pausing to wait for throttle")
          time.sleep(10)
          # for n in track(range(10), description="Pausing..."):
          #   time.sleep(1)
          return generic_post_call(endpoint, params, token)
        if code == 409 or code == 500:
          # Handle duplicate server call error by pausing and trying again
          logging.warning("Throttle limit was reached. Pausing to wait for throttle")
          time.sleep(10)
          return generic_post_call(endpoint, params, token)
        else:
          logging.exception(f"Something broke the script. Code: {code} Error Message: {message} ")

def make_request(method, url, headers, params):
  """Checks which method to use and then makes the request to Space Traders API

  Args:
      method (str): The HTTP method to use
      url (str): The URL of the request
      headers (dict): the request headers holding the Auth
      params (dict): parameters of the request

  Returns:
      Request: Returns the request

  Exceptions:
      Exception: Invalid method - must be GET, POST or PUT
  """
  if method == "POST":
    return requests.post(url, headers=headers, params=params)
  if method == "GET":
    return requests.get(url, headers=headers, params=params)
  if method == "PUT":
    return requests.put(url, headers=headers, params=params)
  else:
    logging.exception(f"Invalid method provided: {method}")

def generic_api_call(method, endpoint, params=None, token=None):
  headers = {'Authorization': 'Bearer ' + token}
  # Make the request to the Space Traders API
  r = make_request(method, URL + endpoint, headers, params)  
  if r.ok:
      return r.json()
  else:
      logging.warning(f"Something went wrong when hitting: {r.request.method} {r.url} with parameters: {params}")
      error = r.json()
      code = error['error']['code']
      message = error['error']['message']
      logging.warning("Error: " + str(error))
      # Check if the error was due to throttline
      if str(code) == '42901':
        # Handle Throttling errors by pausing and trying again
        logging.info("Throttle limit was reached. Pausing to wait for throttle")
        for n in track(range(10), description="Pausing..."):
          time.sleep(1)
        # Recall this method to make the request again. 
        return generic_api_call(method, endpoint, params, token)
      # If not due to throttling raise exception
      else:
        logging.exception(f"Something broke the script. Code: {code} Error Message: {message} ")

def get_user(token, username):
  '''Get the user and return a User Object'''
  # Make a call to the API to retrive the user data
  return User(token, generic_get_call("users/" + username, token=token)['user'])

if __name__ == "__main__":
    # Load Constants
    with open('constants/systems.json', 'r') as infile:
        systems = json.load(infile)
    
    username = "JimHawkins"
    # TOKEN = "4c9f072a-4e95-48d6-bccd-54f1569bd3c5"
    game = Game(systems=systems)
    user = get_user(username, TOKEN)
    print(user.get_ships(as_df=True))

  

