import requests
import pandas as pd
import math
import time
from rich.progress import Progress
import logging

URL = "https://api.spacetraders.io/"
TOKEN = "b33e5ca9-b933-43c3-9249-9fe7ea525fc9"

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
      for dictionary in initial_data:
          for key in dictionary:
              setattr(self, key, dictionary[key])
      for key in kwargs:
          setattr(self, key, kwargs[key])
  
  # Get Good to sell
  def get_cargo_to_sell(self):
    cargo_not_fuel = lambda x: x['good'] != "FUEL"
    cargo_to_sell=filter(cargo_not_fuel,self.cargo)
    return cargo_to_sell

  def get_fuel_level(self):
    fuel = lambda x: x['good'] == "FUEL"
    cargo_fuel=filter(fuel,self.cargo)
    return list(cargo_fuel)[0]['quantity']

class User:
  '''User Object
  
  https://api.spacetraders.io/#api-users'''
  def __init__(self, username, credits, ships, loans):
    self.username = username
    self.credits = credits
    self.ships = ships
    self.loans = loans

  # Get User Details
  def get_user(self):
    return generic_get_call("users/" + self.username)

  def request_loan(self, type):
    # TODO: Return a loan object
    return generic_post_call("users/{0}/loans".format(self.username), params={"type": type})

  def buy_ship(self, location, type):
    # TODO: return a ship object
    return generic_post_call("users/{0}/ships".format(self.username), 
                             params={"location": location, "type": type})
  
  def get_ships(self):
    return [Ship(ship) for ship in self.ships]
  
  def get_ship(self, shipId):
    return Ship(generic_get_call("users/{0}/ships/{1}".format(self.username, shipId))['ship'])

  def new_order(self, shipId, good, quantity):
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
    return math.trunc(hull_capacity / unit_volume)

  def profit_margin(self, good_compare):
    return good_compare['sellPricePerUnit_to'] - good_compare['purchasePricePerUnit_from']

  # Expect DataFrames to be passed to it
  def market_compare(self, from_market, to_market):
    # Convert to DataFrames if String value of Symbol provided
    if isinstance(from_market, str):
      from_market = pd.DataFrame(Game().location(from_market).marketplace())
    if isinstance(to_market, str):
      to_market = pd.DataFrame(Game().location(to_market).marketplace())
    # Do an Inner Join of the Markets on available goods (symbols)
    market_compare = from_market.join(to_market.set_index('symbol'), on="symbol", how="inner", lsuffix="_from", rsuffix="_to")
    # Get the Profit Margins - factoring in volume of the good
    market_compare['profit'] = market_compare.apply(self.profit_margin, axis=1)
    return market_compare
  
  def best_buy(self, from_destination, to_destination):
    # Convert to Location if String value of Symbol provided
    if isinstance(from_destination, str):
      from_destination = Game().location(from_destination)
    if isinstance(to_destination, str):
      to_destination = Game().location(to_destination)
    # Get markets of each destination as DataFrames
    from_market = pd.DataFrame(from_destination.marketplace())
    to_market = pd.DataFrame(to_destination.marketplace())
    # Get the market comparison
    market_comparison = self.market_compare(from_market, to_market)
    # Get the record for the best good - factor in the profit per unit volume
    market_comparison['profit_per_volume'] = market_comparison.apply(lambda x: x['profit'] / x['volumePerUnit_from'], axis=1)
    best_good = market_comparison.loc[market_comparison['profit_per_volume'].idxmax()]
    return {"symbol": best_good['symbol'], "cost": best_good['purchasePricePerUnit_from'], "profit": best_good['profit'], "volume": best_good['volumePerUnit_from']}

  # Returns the best good to buy, how many units to buy of it and the expected profit
  def what_should_I_buy(self, ship, destination):
    # Get the best good to buy
    symbol = self.best_buy(Game().location(ship.location), Game().location(destination))
    # Work out many units to buy
    units_to_buy = self.how_much_to_buy(symbol['volume'], ship.spaceAvailable)
    return {"symbol": symbol['symbol'], "units": units_to_buy, "total_cost": symbol['cost'] * units_to_buy, "expected_profit": symbol['profit'] * units_to_buy}

class Game:
  # See if the game is currently up
  def status(self):
    return generic_get_call("game/status")

  # Get a specific location - returns a location object
  def location(self, symbol):
    return Location(**generic_get_call("game/locations/{0}".format(symbol))['location'])

  def get_available_ships(self, kind=None):
    return generic_get_call("game/ships", params={"class":kind})['ships']

class Location:
  def __init__(self, **kwargs):
      self.__dict__.update(kwargs)
  
  def marketplace(self):
    endpoint = "game/locations/{0}/marketplace".format(self.symbol)
    return generic_get_call(endpoint)['location']['marketplace']

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
        print("Something went wrong")
        print(r.json())

# Generic call to API
def generic_post_call(endpoint, params=None):
    headers = {'Authorization': 'Bearer ' + TOKEN}
    r = requests.post(URL + endpoint, headers=headers, params=params)
    if r.ok:
        return r.json()
    else:
        print("Something went wrong")
        print(r.json())

def get_user(username):
  '''Get the user and return a User Object'''
  # Make a call to the API to retrive the user data
  user = generic_get_call("users/" + username)

  # Pull out the data and return a user object
  username = user['user']['username']
  credits = user['user']['credits']
  ships = user['user']['ships']
  loans = user['user']['loans']
  return User(username, credits, ships, loans)


if __name__ == "__main__":
  username = "JimHawkins"
  game = Game()
  user = get_user(username)
  gravager = user.get_ship('cknegaohp5912821bs6d0ws1xr1')
  jackshaw_prime = user.get_ship('cknei40da11601821bs6lt91ifh3')

  # print(Market().market_compare(gravager.location, "OE-PM"))
  # print(Market().best_buy(gravager.location, "OE-PM-TR"))
  # print(Market().what_should_I_buy(gravager, "OE-PM"))

  # Ideal Flow in one direction
  def trading_run(ship, destination):
    print(R+"Making a trading run with {}. Flying to {}".format(ship.id, destination)+W)
    # Fill up
    if ship.get_fuel_level() < 20:
      print(G+"Filling up Fuel"+W)
      user.new_order(ship.id, "FUEL", 20 - ship.get_fuel_level())
      ship = user.get_ship(ship.id)
    
    # Buy Best Good
    what_to_buy = Market().what_should_I_buy(ship, destination)
    print(G+"Buying {} units of {} for {} with an expected profit of {}".\
      format(what_to_buy['units'], what_to_buy['symbol'], what_to_buy['total_cost'], what_to_buy['expected_profit'])+W)
    user.new_order(ship.id, what_to_buy['symbol'], what_to_buy['units'])
    ship = user.get_ship(ship.id)
    
    # Fly to destination
    user.fly(ship.id, destination, track=True)
    ship = user.get_ship(ship.id)

    # Sell goods
    order = user.sell_order(ship.id, what_to_buy['symbol'], what_to_buy['units'])
    print(G+"Sold {} units of {} at {} with a profit of {}".\
      format(what_to_buy['units'], what_to_buy['symbol'], order['order']['total'], order['order']['total']-what_to_buy['total_cost'])+W)
    ship = user.get_ship(ship.id)
    
    # Return the profit of the run
    return order['order']['total'] - what_to_buy['total_cost']


  profit = []
  for x in range(20):
    if gravager.location == "OE-PM-TR":
      destination = "OE-PM"
    if gravager.location == "OE-PM":
      destination = "OE-PM-TR"
    profit.append(trading_run(gravager, destination))
    # Update Gravager
    gravager = user.get_ship(gravager.id)
  
  print("Total money made: " + str(sum(profit)))

  # if gravager.location == "OE-PM-TR":
  #     destination = "OE-PM"
  # if gravager.location == "OE-PM":
  #     destination = "OE-PM-TR"
  
  # trading_run(gravager, destination)
  # user.fly(gravager.id, destination, track=True)
  # user.sell_order(gravager.id, "DRONES", 41)


  # Buy a Jackshaw
  # ships_to_buy = pd.DataFrame(game.get_available_ships("MK-I"))
  # jacksaw_mask = ships_to_buy['manufacturer'] == "Jackshaw"
  # print(ships_to_buy.loc[jacksaw_mask], ships_to_buy.loc[jacksaw_mask].purchaseLocations.values)
  # print(user.buy_ship('OE-PM-TR', 'JW-MK-I'))


  

