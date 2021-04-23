import sqlite3
import sqlalchemy
import logging
import pandas as pd

DATABASE_LOCATION = 'sqlite:////Users/zachooper/Documents/Personal/Projects/SpaceTraders/spaceTraders/SpaceTraders_DB.sqlite'


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Init engine, conn & cursor
engine = sqlalchemy.create_engine(DATABASE_LOCATION)

def write_to_db(df, table, create_table_sql):
  conn = sqlite3.connect('/Users/zachooper/Documents/Personal/Projects/SpaceTraders/spaceTraders/SpaceTraders_DB.sqlite')
  logging.debug("Connecting to Database: 'SpaceTraders_DB.sqlite'")
  cursor = conn.cursor()
  # Create Table if not already created
  cursor.execute(create_table_sql)
  logging.debug("Connected to Database")

  # Add the data to the DB
  try:
    logging.info("Adding {0} records to table: {1}".format(len(df), table))
    df.to_sql(table, engine, index=False, if_exists="append")
  except Exception as e:
    logging.warning(e)
    logging.warning("Data already exists in the database. {0} records not added to Database".format(len(df)))

  # Close the DB
  conn.close()
  logging.debug("Diconnected from Database")

def write_marketplace_to_db(marketplace):
  table = "marketplace_tracker"
  sql_query = """
  CREATE TABLE IF NOT EXISTS marketplace_tracker(
    time VARCHAR(200),
    location VARCHAR(200),
    symbol VARCHAR(200),
    volumePerUnit VARCHAR(200),
    pricePerUnit VARCHAR(200),
    purchasePricePerUnit VARCHAR(200),
    sellPricePerUnit VARCHAR(200),
    quantityAvailable VARCHAR(200),
    CONSTRAINT primary_key_constraint PRIMARY KEY (time)
  )
  """
  write_to_db(marketplace, table, sql_query)


def write_buy_order_to_db(order):
  table = "buy_orders"
  sql_query = """
  CREATE TABLE IF NOT EXISTS buy_orders (
    time VARCHAR(200),
    location VARCHAR(200),
    symbol VARCHAR(200),
    units INT,
    cost INT,
    total_cost INT,
    profit INT,
    profit_per_volume INT,
    expected_profit INT,
    sell_location VARCHAR(200),
    CONSTRAINT primary_key_constraint PRIMARY KEY (time)
  )
  """
  write_to_db(order, table, sql_query)


def write_sell_order_to_db(order):
  table = "sell_orders"
  sql_query = """
  CREATE TABLE IF NOT EXISTS sell_orders (
    time VARCHAR(200),
    location VARCHAR(200),
    symbol VARCHAR(200),
    units INT,
    sell_price INT,
    total_sell_amount INT,
    expected_profit INT,
    buy_location VARCHAR(200),
    CONSTRAINT primary_key_constraint PRIMARY KEY (time)
  )
  """
  write_to_db(order, table, sql_query)

def write_flight_path_to_db(flightPath):
  table = "flight_paths"
  sql_query = """
  CREATE TABLE IF NOT EXISTS flight_paths (
    time VARCHAR(200),
    from_loc VARCHAR(200),
    to_loc VARCHAR(200),
    distance INT,
    estimated_fuel_required INT,
    actual_fuel_required INT,
    time_taken INT,
    ship_manufactorer VARCHAR(200),
    ship_type VARCHAR(200),
    speed INT,
    totalVolume INT,
    plating INT,
    weapons INT,
    flight_reason VARCHAR(200),
    CONSTRAINT primary_key_constraint PRIMARY KEY (time)
  )
  """
  write_to_db(flightPath, table, sql_query)

def get_market_tracker():
  market_tracker = pd.read_sql('marketplace_tracker', engine)
  market_tracker['purchasePricePerUnit'] = market_tracker['purchasePricePerUnit'].astype(int)
  market_tracker['sellPricePerUnit'] = market_tracker['sellPricePerUnit'].astype(int)
  market_tracker['quantityAvailable'] = market_tracker['quantityAvailable'].astype(int)
  market_tracker['pricePerUnit'] = market_tracker['pricePerUnit'].astype(int)
  market_tracker['volumePerUnit'] = market_tracker['volumePerUnit'].astype(int)
  market_tracker['time'] = pd.to_datetime(market_tracker['time'])
  return market_tracker

def get_flight_paths():
  flight_paths = pd.read_sql('flight_paths', engine)
  return flight_paths

def get_buy_orders():
  buy_orders = pd.read_sql('buy_orders', engine)
  return buy_orders

def get_sell_orders():
  sell_orders = pd.read_sql('sell_orders', engine)
  return sell_orders