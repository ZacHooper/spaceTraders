import sqlite3
import sqlalchemy
import pandas as pd

DATABASE_LOCATION = 'sqlite:///SpaceTraders_DB.sqlite'

engine = sqlalchemy.create_engine(DATABASE_LOCATION)
conn = sqlite3.connect('SpaceTraders_DB.sqlite')

def get_market_tracker():
  market_tracker = pd.read_sql('marketplace_tracker', engine)
  market_tracker['purchasePricePerUnit'] = market_tracker['purchasePricePerUnit'].astype(int)
  market_tracker['sellPricePerUnit'] = market_tracker['sellPricePerUnit'].astype(int)
  market_tracker['quantityAvailable'] = market_tracker['quantityAvailable'].astype(int)
  market_tracker['pricePerUnit'] = market_tracker['pricePerUnit'].astype(int)
  market_tracker['volumePerUnit'] = market_tracker['volumePerUnit'].astype(int)
  market_tracker['time'] = pd.to_datetime(market_tracker['time'])
  return market_tracker