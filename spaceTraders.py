import requests
import pandas as pd
import math
import time
import json
from rich.progress import Progress, track
import logging
from os import getcwd

URL = "https://api.spacetraders.io/"
TOKEN = "4c9f072a-4e95-48d6-bccd-54f1569bd3c5"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

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
  def __init__(self, *initial_data, **kwargs):
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
    logging.info("Updating Cargo & Space Available of ship: {0}. Previous Cargo: {1}. New Cargo: {2}. Previous Space Available: {3}. New Space Available: {4}".format(self.id, self.cargo, new_cargo, self.spaceAvailable, new_spaceAvailable))
    self.cargo = new_cargo
    self.spaceAvailable = new_spaceAvailable
    return True

  def update_location(self, new_x, new_y, new_location):
    logging.info("Updating location of ship. Previous Location: {0}. Previous X: {1}. Previous Y: {2}. New Location: {3}, New X: {4}, New Y: {5}".\
      format(self.location, self.x, self.y, new_location, new_x, new_y))
    self.location = new_location
    self.x = new_x
    self.y = new_y
    return True

  def calculate_fuel_usage(self, *args):
    '''
    NOT A PERFECT RESULT

    Based on the distance provided to a location works out the estimated fuel required to fly there

    USAGE:
    Provide already calculated distance 
    OR
    Provide the x & y coordinates of the destination
    '''
    calc_fuel = lambda d, extra: round((9/37) * d + 4 + extra)

    # Distance supplied
    if len(args) == 1:
      # Handle extra required for Class 2 Gravs
      if self.type == "GR-MK-II":
        return calc_fuel(args[0], 2)
      if self.type == "GR-MK-III":
        return calc_fuel(args[0], 4)

      return calc_fuel(args[0], 0)
    if len(args) == 2:
      # Handle extra required for Class 2 Gravs
      if self.type == "GR-MK-II":
        return calc_fuel(self.calculate_distance(args[0], args[1]), 2)
      if self.type == "GR-MK-III":
        return calc_fuel(self.calculate_distance(args[0], args[1]), 4)
      return calc_fuel(self.calculate_distance(args[0], args[1]), 0)
    
  
  def calculate_distance(self, to_x, to_y):
    return round(math.sqrt(math.pow((to_x - self.x),2) + math.pow((to_y - self.y),2)))

  def get_closest_location(self):
    """
    Returns a tuple containing the clostest location to the ship
    
    [0]: A Location object of the closet location
    [1]: Distance to the location
    """
    locations = Game().locations
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
  def __init__(self, username, credits, ships, loans, full_json):
    self.username = username
    self.credits = credits
    self.ships = self.get_ships(ships)
    self.loans = loans
    self.full_json = full_json

  def request_loan(self, type):
    '''
    API CALL: https://api.spacetraders.io/#api-loans-NewLoan
    '''
    # TODO: Return a loan object
    return generic_post_call("users/{0}/loans".format(self.username), params={"type": type})

  def buy_ship(self, location, type):
    '''
    API CALL: https://api.spacetraders.io/#api-ships-NewShip
    '''
    # TODO: return a ship object
    # Update the 'ships' attribute of the user
    return generic_post_call("users/{0}/ships".format(self.username), 
                             params={"location": location, "type": type})
  
  def get_ships(self, ships=None, as_df=False, fields=None, sort_by=None, filter_by=None):
    '''
    Returns a list of Ship objects that the user currently owns
    '''
    if ships is not None:
      return [Ship(ship) for ship in ships]

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

      

    #   return df

    return return_ships
  
  def get_ship(self, shipId):
    '''
    Returns a Ship object for the shipId provided. 
    
    :Param shipId : str
    :Return ship : Ship 
    '''
    return next((ship for ship in self.ships if ship.id == shipId), None)

  def get_trackers(self):
    '''
    Returns a list of all the Jackshaw "Tracker" ships.
    Jackshaws are the cheapest ship type and are used to station at each location for marketplace tracking.
    '''
    tracker_ships = lambda x: x.manufacturer == "Jackshaw"
    trackers=list(filter(tracker_ships, self.ships))
    return trackers

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
    order = generic_post_call(endpoint, params=params)
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
    order = generic_post_call(endpoint, params=params)
    # Log the result
    logging.info("Selling {0} units of {1} for {2} at {3}. Remaining credits: {4}. Offloading Goods from ship: {5}"\
      .format(order['order']['quantity'], order['order']['good'], 
              order['order']['total'], order['ship']['location'],
              order['credits'], shipId))
    return order

  def fly(self, shipId, destination, track=False):
    endpoint = "users/{0}/flight-plans".format(self.username)

    # Track the flights progress in the console
    if track:
      flight = generic_post_call(endpoint, params={"shipId": shipId,
                                                   "destination": destination})['flightPlan']
      logging.info("Ship {0} has left {1} and is flying to {2}".format(shipId, flight['departure'], destination))
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
      
    return generic_post_call(endpoint, params={
      "shipId": shipId,
      "destination": destination
    })

  def flight(self, flightPlanId):
    return generic_get_call("users/{0}/flight-plans/{1}".format(self.username, flightPlanId))

class Loan:
  def __init__(self, id, due, repaymentAmount, status, type):
    self.id = id
    self.due = due
    self.repaymentAmount = repaymentAmount
    self.status = status
    self.type = type

class Market:
  def how_much_to_buy(self, unit_volume, hull_capacity):
    '''Returns max amount of units that can fit into the ship'''
    return math.trunc(hull_capacity / unit_volume)

  def profit_margin(self, good_compare):
    return good_compare['sellPricePerUnit_to'] - good_compare['purchasePricePerUnit_from']

  # Expect DataFrames to be passed to it
  def market_compare(self, from_market, to_market):
    """Returns a DataFrame with matching Goods and the profit made/lost if sold from the 'from_market' to the 'to_market'"""
    # Convert to DataFrames if String value of Symbol provided
    if isinstance(from_market, str):
      from_market = pd.DataFrame(Game().location(from_market).marketplace())
    if isinstance(to_market, str):
      to_market = pd.DataFrame(Game().location(to_market).marketplace())
    # Do an Inner Join of the Markets on available goods (symbols)
    market_compare = from_market.join(to_market.set_index('symbol'), on="symbol", how="inner", lsuffix="_from", rsuffix="_to")
    # Get the Profit Margins - factoring in volume of the good
    market_compare['profit'] = market_compare.apply(self.profit_margin, axis=1)
    market_compare['profit_per_volume'] = market_compare.apply(lambda x: x['profit'] / x['volumePerUnit_from'], axis=1)
    return market_compare
  
  def best_buy(self, from_market, to_market):
    """Returns a JSON object with the best Good to buy at the 'from_destination' if wanting to sell goods at the 'to_destination'"""
    # Convert to Location and get market if String value of Symbol provided
    if isinstance(from_market, str):
      from_market = pd.DataFrame(Game().location(from_market).marketplace())
    if isinstance(to_market, str):
      to_market = pd.DataFrame(Game().location(to_market).marketplace())
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
    loc = Game().locations[destination]
    # Get the best good to buy
    if ship_marketplace is None:
      logging.debug("Getting the best goods to trade for from {0} to {1} - Ships Marketplace not supplied".format(ship.location, loc.symbol))
      best_good = self.best_buy(ship.location, loc.symbol)
    else:
      logging.debug("Getting the best goods to trade for from {0} to {1} - Ships Marketplace supplied".format(ship.location, loc.symbol))
      best_good = self.best_buy(pd.DataFrame(ship_marketplace), loc.symbol)
    # How much fuel would be required
    fuel_required = ship.calculate_fuel_usage(loc.x, loc.y)
    logging.debug("Estimated fuel required from {0} to {1} is: {2}".format(ship.location, loc.symbol, fuel_required))
    # Work out many units to buy
    units_to_buy = self.how_much_to_buy(best_good['volume'], ship.maxCargo - fuel_required)
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
  def __init__(self, systems_path=None):
    self.systems = self.load_sytems() if systems_path is None else self.load_sytems(systems_path)
    self.locations = self.load_locations()
  # See if the game is currently up
  def status(self):
    """Returns whether the game is Up or Not"""
    return generic_get_call("game/status")

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
    return generic_get_call("game/ships", params={"class":kind})['ships']

  def calculate_distance(from_x, from_y, to_x, to_y):
    return round(math.sqrt(math.pow((to_x - from_x),2) + math.pow((to_y - from_y),2)))
  
  def calculate_fuel_usage(self, distance):
    '''
    NOT A PERFECT RESULT

    Based on the distance provided to a location works out the estimated fuel required to fly there
    '''
    return round((9/37) * distance + 2 + 2)

  def load_sytems(self, systems_path=None):
    '''
    This will simply load the complete JSON file with no further transformations
    '''
    # Path handling to account for non relative path usage
    path = 'systems.json' if systems_path is None else systems_path
    with open(path, 'r') as infile:
      return json.load(infile)
  
  def load_locations(self):
    '''
    This will return a dict of Location objects for all the locations across both systems. The key is the locations symbol.
    '''
    # Return each location as an object with it's symbol as the key
    return {loc['symbol']: Location(**loc) for sys in self.systems for loc in sys['locations']}


class Location:
  def __init__(self, **kwargs):
      self.__dict__.update(kwargs)
  
  def marketplace(self):
    endpoint = "game/locations/{0}/marketplace".format(self.symbol)
    return generic_get_call(endpoint)['location']['marketplace']
  
  def __repr__(self):
    return "Symbol: " + self.symbol + ", Name: " + self.name

  def __str__(self):
    return "Symbol: " + self.symbol + ", Name: " + self.name

# Get New User 
def post_create_user(username):
  endpoint = "users/{0}/".format(username)
  return generic_post_call(endpoint, params=None)

# Misc Functions
# Generic get call to API
def generic_get_call(endpoint, params=None):
    headers = {'Authorization': 'Bearer ' + TOKEN}
    r = requests.get(URL + endpoint, headers=headers, params=params)
    if r.ok:
        return r.json()
    else:
        logging.warning("Something went wrong when hitting: {0} with parameters: {1}".format(URL+endpoint, params))
        logging.warning("Error: " + str(r.json()))
        # Handle Throttling errors by pausing and trying again
        logging.info("Pausing to wait for throttle")
        for n in track(range(10), description="Pausing..."):
          time.sleep(1)
        return generic_get_call(endpoint, params)


# Generic call to API
def generic_post_call(endpoint, params=None):
    headers = {'Authorization': 'Bearer ' + TOKEN}
    r = requests.post(URL + endpoint, headers=headers, params=params)
    if r.ok:
        return r.json()
    else:
        logging.warning("Something went wrong when hitting: {0} with parameters: {1}".format(URL+endpoint, params))
        logging.warning("Error: " + str(r.json()))
        # Handle Throttling errors by pausing and trying again
        logging.info("Pausing to wait for throttle")
        for n in track(range(10), description="Pausing..."):
          time.sleep(1)
        return generic_post_call(endpoint, params)

def get_user(username):
  '''Get the user and return a User Object'''
  # Make a call to the API to retrive the user data
  user = generic_get_call("users/" + username)

  # Pull out the data and return a user object
  username = user['user']['username']
  credits = user['user']['credits']
  ships = user['user']['ships']
  loans = user['user']['loans']
  return User(username, credits, ships, loans, user)


if __name__ == "__main__":
  username = "JimHawkins"
  game = Game()
  user = get_user(username)
  print(user.get_ships(as_df=True))
  user.sell_order()

  

