# Use DBeaver to view db

import SpaceTraders as st
import pandas as pd
import datetime
import sqlite3
import sqlalchemy
import logging
import time
from rich.progress import track

DATABASE_LOCATION = 'sqlite:///SpaceTraders_DB.sqlite'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def write_marketplace_to_db(marketplace, location):
  # Add a unique time to every record
  def get_time_now():
    time.sleep(.00001)
    return datetime.datetime.now()

  marketplace['time'] = [get_time_now() for _ in range(len(marketplace.index))]
  marketplace['location'] = location

  # Drop the spread column as it's not needed
  if 'spread' in marketplace.columns:
    marketplace = marketplace.drop('spread', axis=1)
  
  # --- Load to DB ---

  # Init engine, conn & cursor
  engine = sqlalchemy.create_engine(DATABASE_LOCATION)
  conn = sqlite3.connect('SpaceTraders_DB.sqlite')
  logging.info("Connecting to Database: 'SpaceTraders_DB.sqlite'")
  cursor = conn.cursor()

  # Create Table if not already created
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
  
  cursor.execute(sql_query)
  logging.info("Connected to Database")

  # Add the data to the DB
  try:
    logging.info("Adding {0} records to table: marketplace_tracker".format(len(marketplace)))
    marketplace.to_sql("marketplace_tracker", engine, index=False, if_exists="append")
  except Exception as e:
    logging.warning(e)
    logging.warning("Data already exists in the database. {0} records not added to Database".format(len(marketplace)))

  # Close the DB
  conn.close()
  logging.info("Diconnected from Database")

def get_trackers(ships):
    tracker_ships = lambda x: x.manufacturer == "Jackshaw"
    trackers=filter(tracker_ships, ships)
    return trackers

def track_markets(repeat):
  get_marketplace = lambda x: pd.DataFrame(st.Game().location(x).marketplace())
  user = st.get_user("JimHawkins")
  trackers = get_trackers(user.get_ships())
  tracker_locations = [tracker.location for tracker in trackers]
  for x in range(repeat):
    for loc in tracker_locations:
      logging.info("Premptive pause for throttle")
      for n in track(range(5), description="Pausing..."):
        time.sleep(1)
      print("Adding Market Records for: " + loc)
      write_marketplace_to_db(get_marketplace(loc), loc)
    logging.info("Sleeping")
    for n in track(range(60), description="Sleeping..."):
      time.sleep(1)
    

if __name__ == "__main__":
  track_markets(1)

  


  
  
  
  