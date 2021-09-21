
#%%
import pandas as pd
import csv
import numpy as np
from trading_calendars import get_calendar
from zipline.utils.calendars import TradingCalendar
from zipline.utils.tradingcalendar import get_trading_days
from pandas import Timestamp


#%%
#This is the process to get the correct trading days, which will then be use in the Bundle Ingest process to index the days
trading_days = get_trading_days(start=Timestamp('2005-01-03 00:00:00+0000', tz='UTC'), 
                                end=Timestamp('2020-10-26 02:21:29.456875+0000')
                                ).date.astype(str)

# %%
# US Markets Closed December 5, 2018: National Day of Mourning for George H.W. Bush
trading_days = np.delete(trading_days, np.where(trading_days == '2018-12-05'))
trading_days[trading_days == '2018-12-05']


#%%
# Create a CSV file to set the Zipline Bundle Ingest process against
with open('trading_calendar.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(trading_days)
# %%
