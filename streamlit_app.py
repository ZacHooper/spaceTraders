import streamlit as sl
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import SpaceTraders as st
from db_handler import get_market_tracker

game = st.Game()

# Display the different planets in a table
sl.title("OE System")
OE = pd.DataFrame(game.systems[0]['locations'])
OE

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
metals = market['symbol'] == good

fig = plt.figure()
loc_with_good = market.loc[metals]

for loc in loc_with_good.location.unique():
    loc_mask = market['location'] == loc
    loc_good_df = loc_with_good.loc[loc_mask]
    plt.plot(loc_good_df.time, loc_good_df.purchasePricePerUnit, label = loc)

plt.legend()
sl.pyplot(fig)

# 



