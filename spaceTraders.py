import requests
import pandas as pd

URL = "https://api.spacetraders.io/"
TOKEN = "b33e5ca9-b933-43c3-9249-9fe7ea525fc9"

class Ship:
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
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  # Get Good to sell
  def get_cargo_to_sell():
    cargo_not_fuel = lambda x: x['good'] != "FUEL"
    cargo_to_sell=filter(cargo_not_fuel,self.cargo)
    return cargo_to_sell

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
    return [Ship(**ship) for ship in self.ships]
  
  def get_ship(self, shipId):
    for ship in self.ships:
      if ship['id'] == shipId:
        return Ship(**ship) 

  def new_order(self, shipId, good, quantity):
    endpoint = "users/{0}/purchase-orders".format(self.username)
    return generic_post_call(endpoint, params={
      "shipId": shipId,
      "good": good,
      "quantity": quantity
    })

  def sell_order(self, shipId, good, quantity):
    endpoint = "users/{0}/sell-orders".format(self.username)
    return generic_post_call(endpoint, params={
      "shipId": shipId,
      "good": good,
      "quantity": quantity
    })

  def fly(self, shipId, destination):
    endpoint = "users/{0}/flight-plans".format(self.username)
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
  def how_much_to_buy(unit_volume, hull_capacity):
    return math.trunc(hull_capacity / unit_volume)

  # Expect DataFrames to be passed to it
  def market_compare(from_market, to_market):
    # Do an Inner Join of the Markets on available goods (symbols)
    market_compare = from_market.join(to_market.set_index('symbol'), on="symbol", how="inner", lsuffix="_from", rsuffix="_to")
    # Get the Profit Margins - factoring in volume of the good
    market_compare['profit'] = market_compare.apply(profit_margin, axis=1)
    return market_compare
  
  def best_buy(from_destination, to_destination):
    # Get Markets of each destination as DataFrames
    from_market = pd.DataFrame(from_destination.marketplace())
    to_market = pd.DataFrame(to_destination.marketplace())
    # Get the market comparison
    market_comparison = market_compare(from_market, to_market)
    # Get the record for the best good
    best_good = market_comparison.loc[market_comparison['profit'].idxmax()]
    return {"symbol": best_good['symbol'], "profit": best_good['profit'], "volume": best_good['volumePerUnit_from']}

  # Returns the best good to buy, how many units to buy of it and the expected profit
  def what_should_I_buy(ship, destination):
    # Get the best good to buy
    symbol = best_buy(st.Game.location(ship.location), st.Game.location(destination))
    # Work out many units to buy
    units_to_buy = how_much_to_buy(symbol['volume'], 80)
    return {"symbol": symbol['symbol'], "units": units_to_buy, "profit": symbol['profit'] * units_to_buy}

class Game:
  # See if the game is currently up
  def status():
    return generic_get_call("game/status")

  # Get a specific location - returns a location object
  def location(symbol):
    return Location(**generic_get_call("game/locations/{0}".format(symbol))['location'])

  def get_available_ships(kind=None):
    return generic_get_call("game/ships", params={"class":kind})

class Location:
  def __init__(self, **kwargs):
      self.__dict__.update(kwargs)
  
  def marketplace(self, ):
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

  user = get_user(username)
  ships = [Ship(**ship) for ship in user.get_ships()['ships']]
  ship = ships[1]
  
  # Planets

  tritus = Game.location("OE-PM-TR")
  prime = Game.location("OE-PM")


  # Buy Fuel
  # print(user.new_order(ship.id, "FUEL", 20))

  # Buy Ship parts
  # print(user.new_order(ship.id, "SHIP_PLATING", 40)) # spent 3720

  # Sell Ship Parts
  # print(user.sell_order(ship.id, "SHIP_PLATING", 40)) # sold for 5920
  
  # Marketplace
  print(pd.DataFrame(tritus.marketplace()))
  print(pd.DataFrame(prime.marketplace()))

  # Flying
  # print(user.fly(ship.id, tritus.symbol))
  # print(user.fly(ship.id, prime.symbol))
  # print(user.flight('cknejn0a216720571bs6shmigpy1'))

    
  

