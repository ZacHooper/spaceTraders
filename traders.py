import SpaceTraders as st
import datetime
import time
import trackers

URL = "https://api.spacetraders.io/"
TOKEN = "b33e5ca9-b933-43c3-9249-9fe7ea525fc9"
username = "JimHawkins"

user = st.get_user(username)
game = st.Game()

# Colours
R  = '\033[31m' # red
G  = '\033[32m' # green
W  = '\033[0m'  # white (normal)

def trading_run(ship, destination):
    print(R+"Making a trading run with {}. Flying to {}".format(ship.id, destination)+W)
    # Fill up
    if ship.get_fuel_level() < 20:
      print(G+"Filling up Fuel"+W)
      user.new_order(ship.id, "FUEL", 20 - ship.get_fuel_level())
      ship = user.get_ship(ship.id)
    
    # Buy Best Good
    what_to_buy = st.Market().what_should_I_buy(ship, destination)
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

def get_locations_being_tracked(ships=None):
    if ships is None:
        ships = user.get_ships()
    tracker_ships = trackers.get_trackers(ships)
    return [ship.location for ship in tracker_ships]

def find_optimum_trade_route(ship):
    # Get tracked markets and remove the current market
    all_tracker_locs = get_locations_being_tracked()
    # remove current market of ship
    all_tracker_locs.remove(ship.location)

    # Work out the best trade
    potential_trades = [st.Market().what_should_I_buy(ship, loc) for loc in all_tracker_locs]
    # Pair up loc with best trade
    pt_loc = list(zip(all_tracker_locs, potential_trades))
    # Return trade with Max expected profit
    return max(pt_loc, key=lambda d: d[1]['expected_profit']) 

def any_dest_trading_run(ship):
    # fill up 
    if ship.get_fuel_level() < 30:
      print(G+"Filling up Fuel"+W)
      # Place order
      fuel_order = user.new_order(ship.id, "FUEL", 30 - ship.get_fuel_level())
      # Update ship
      ship.update_cargo(fuel_order['ship']['cargo'], fuel_order['ship']['spaceAvailable'])

    # Work out good to buy and destination
    trade_route = find_optimum_trade_route(ship)
    print(G+"Buying {} units of {} for {} with an expected profit of {}".\
      format(trade_route[1]['units'], trade_route[1]['symbol'], trade_route[1]['total_cost'], trade_route[1]['expected_profit'])+W)

    # Place order
    buy_order = user.new_order(ship.id, trade_route[1]['symbol'], trade_route[1]['units'])
    # Update Ship
    ship.update_cargo(buy_order['ship']['cargo'], buy_order['ship']['spaceAvailable'])

    # Fly to destination
    flight = user.fly(ship.id, trade_route[0], track=True)
    # Update Ship
    ship = user.get_ship(ship.id)

    # Sell Goods
    sell_order = user.sell_order(ship.id, trade_route[1]['symbol'], trade_route[1]['units'])
    print(G+"Sold {} units of {} at {} with a profit of {}".\
      format(trade_route[1]['units'], trade_route[1]['symbol'], sell_order['order']['total'], sell_order['order']['total']-trade_route[1]['total_cost'])+W)
    # Update Ship
    ship.update_cargo(sell_order['ship']['cargo'], sell_order['ship']['spaceAvailable'])

    return sell_order['order']['total'] - trade_route[1]['total_cost']

def any_dest_trading_run2(ship):
  # fill up 
  if ship.get_fuel_level() < 30:
    print(G+"Filling up Fuel"+W)
    # Place order
    fuel_order = user.new_order(ship.id, "FUEL", 30 - ship.get_fuel_level())
    # Update ship
    ship.update_cargo(fuel_order['ship']['cargo'], fuel_order['ship']['spaceAvailable'])

  # Work out good to buy and destination
  trade_route = find_optimum_trade_route(ship)
  print(G+"Buying {} units of {} for {} with an expected profit of {}".\
    format(trade_route[1]['units'], trade_route[1]['symbol'], trade_route[1]['total_cost'], trade_route[1]['expected_profit'])+W)

  # Place order
  buy_order = user.new_order(ship.id, trade_route[1]['symbol'], trade_route[1]['units'])
  # Update Ship
  ship.update_cargo(buy_order['ship']['cargo'], buy_order['ship']['spaceAvailable'])

  # Fly to destination
  flight = user.fly(ship.id, trade_route[0], track=True)
  # Update Ship
  ship = user.get_ship(ship.id)

  # Sell Goods
  sell_order = user.sell_order(ship.id, trade_route[1]['symbol'], trade_route[1]['units'])
  print(G+"Sold {} units of {} at {} with a profit of {}".\
    format(trade_route[1]['units'], trade_route[1]['symbol'], sell_order['order']['total'], sell_order['order']['total']-trade_route[1]['total_cost'])+W)
  # Update Ship
  ship.update_cargo(sell_order['ship']['cargo'], sell_order['ship']['spaceAvailable'])

  return sell_order['order']['total'] - trade_route[1]['total_cost']

if __name__ == "__main__":
  gravager = user.get_ship('cknegaohp5912821bs6d0ws1xr1')
  
  # Get the 
  start = datetime.datetime.now()
  profit = []

  profit.append(any_dest_trading_run2(gravager))
  
  print("Total money made: " + str(sum(profit)))
  now = datetime.datetime.now() - start
  print("Time taken: " + str(now))
  profit_per_hour = round( sum(profit) / (now.total_seconds() / 3600), 2)
  print("Profit per Hour: " + str(profit_per_hour))

  