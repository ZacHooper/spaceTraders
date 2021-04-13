import SpaceTraders as st
import datetime
import time

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

if __name__ == "__main__":
  gravager = user.get_ship('cknegaohp5912821bs6d0ws1xr1')
  
  # Get the 
  start = datetime.datetime.now()
  profit = []
  # Runs the trading run function 50 times
  # Changes the direction automatically
  for x in range(20):
    print("Trading run: " + str(x) + " Profit so far: " + str(sum(profit)))
    if gravager.location == "OE-PM-TR":
      destination = "OE-PM"
    if gravager.location == "OE-PM":
      destination = "OE-PM-TR"
    profit.append(trading_run(gravager, destination))
    # Update Gravager
    gravager = user.get_ship(gravager.id)
  
  print("Total money made: " + str(sum(profit)))
  now = datetime.datetime.now() - start
  print("Time taken: " + str(now))
  profit_per_hour = round( sum(profit) / (now.total_seconds() / 3600), 2)
  print("Profit per Hour: " + str(profit_per_hour))

  