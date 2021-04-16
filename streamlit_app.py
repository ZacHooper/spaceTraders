import streamlit as sl
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import SpaceTraders as st
from db_handler import get_market_tracker

game = st.Game()
user = st.get_user("JimHawkins")

sl.title("Hi, " + user.username)

# Display the different planets in a table
sl.title("OE System")
OE = pd.DataFrame(game.systems[0]['locations'])
OE

fig, ax = plt.subplots(figsize=(12,12))
ax.scatter(OE.x, OE.y)
OE[['x','y','name']].apply(lambda x: ax.text(*x),axis=1)
sl.pyplot(fig)

# Display the entire Market Tracker Database
sl.title("Market Tracker")
market = get_market_tracker()
market

# Plot how the sell price of a good on each planet has changed over time
"""
# Sell Price of Goods Over Time
*Use the dropdown to select the good to graph*
"""
good = sl.selectbox('Select', market.symbol.unique())
good_mask = market['symbol'] == good

fig = plt.figure()
loc_with_good = market.loc[good_mask]

for loc in loc_with_good.location.unique():
    loc_mask = market['location'] == loc
    loc_good_df = loc_with_good.loc[loc_mask]
    plt.plot(loc_good_df.time, loc_good_df.purchasePricePerUnit, label = loc)

plt.legend()
sl.pyplot(fig)

# Plot how the sell price of a good on each planet has changed over time
"""
# Buy & Sell Price Comparison
*Use the dropdowns to select the good and location*
"""
location = sl.selectbox('Location Select', market.location.unique())
location_mask = market['location'] == location
good2 = sl.selectbox('Good Selectno', market.loc[location_mask].symbol.unique())
loc_good_mask = (market['symbol'] == good2) & (location_mask)

fig = plt.figure()
loc_with_good = market.loc[loc_good_mask]

plt.plot(loc_with_good.time, loc_with_good.sellPricePerUnit, label = "Sell Price")
plt.plot(loc_with_good.time, loc_with_good.purchasePricePerUnit, label = "Buy Price")

plt.legend()
sl.pyplot(fig)

# Ships
ships = user.full_json['user']['ships']
ships_df = pd.DataFrame(ships)

"""
## Traders
"""
traders_mask = ships_df.manufacturer == "Gravager"
ships_df.loc[traders_mask,['id', 'location', 'class']]

