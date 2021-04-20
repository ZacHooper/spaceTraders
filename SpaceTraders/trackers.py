# Use DBeaver to view db

import pandas as pd
import datetime
import logging
import time
from SpaceTraders import core, db_handler
from rich.progress import track

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
  db_handler.write_marketplace_to_db(marketplace)

def get_trackers(ships):
    tracker_ships = lambda x: x.manufacturer == "Jackshaw"
    trackers=filter(tracker_ships, ships)
    return trackers

def track_markets(repeat):
  get_marketplace = lambda x: pd.DataFrame(core.Game().location(x).marketplace())
  user = core.get_user("JimHawkins")
  trackers = get_trackers(user.get_ships())
  tracker_locations = [tracker.location for tracker in trackers]
  for x in range(repeat):
    for loc in tracker_locations:
      print("Adding Market Records for: " + loc)
      write_marketplace_to_db(get_marketplace(loc), loc)
      logging.info("Premptive pause for throttle")
      for n in track(range(5), description="Pausing..."):
        time.sleep(1)
    logging.info("Sleeping")
    for n in track(range(60), description="Sleeping..."):
      time.sleep(1)
    

if __name__ == "__main__":
  track_markets(1)

  


  
  
  
  