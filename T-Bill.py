# Importing required modules
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import *
import numpy as np
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.dates as md
import random
from matplotlib import cm 
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as dates
import matplotlib.ticker as ticker

# # Opening file containing data.
inFile = open("data2.csv")
dataFile = pd.read_csv(inFile, index_col=0, parse_dates="True")
print "Data has been read."

# Parsing HTML
url = "http://www.wsj.com/mdc/public/page/2_3020-tstrips.html"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

# Creating empty variables to scrape data into.
maturity = []
bidPrice = []
dtm = []
ytm = []
exp = []


# Creating an object of the first object that is a dataframe.
table = soup.find(class_='mdcTable')
# Finding all the <tr> tag pairs, less the first few.
for row in table.find_all('tr')[75:207]:
    # Create a variable of all the <td> tag pairs within each <tr> pair
    col = row.find_all('td')
    # Create variable of string inside first column.
    col1 = col[0].string.strip()
    # and then add to the appropriate variable.
    maturity.append(col1)
    # create var of float inside second column.
    col2 = col[1].string.strip()
    bidPrice.append(col2)


# Formatting dates and calculating days to maturity
start = datetime.today().date()

for item in maturity:
    date = datetime.strptime(item, "%Y %b %d").date()
    days = date - start
    dtm.append(days)
    ytm.append([])

# Creating the data frame.

# Makes todays date into a string so that we can differentiate columns as they are appended to the data set.
t = str(start)
today = datetime.strptime(t, '%Y-%m-%d').strftime('%m/%d/%Y')


# Naming columns for dataframe 
columns = {'maturity': maturity, 'bidPrice': bidPrice, 'dtm': dtm, 'ytm': ytm, 'day': today}

df = pd.DataFrame(columns)


# Changing datatypes
df['bidPrice'] = pd.to_numeric(df['bidPrice'], errors="ignore")
df['ytm'] = pd.to_numeric(df['ytm'], errors="ignore")
df['dtm'] = df['dtm'] / np.timedelta64(1, 'D')

# Calculating yield
df['ytm'] = (100.0/df['bidPrice'])**((1/df['dtm'])*365)-1

# Adding today's data to master file.
# frames = [dataFile, df]
results = dataFile.append(df, ignore_index=True)


# Writing new dataframe to csv file. This write the ENTIRE dataset over again so don't mess it up.
results.to_csv('data2.csv', mode='w')
print "Data file updated."

# Making the graph --  right now this only does the most current day. 

csv = open("data2.csv")
df = pd.read_csv(csv, sep=',')
print "Data file read."

df.head()

def format_date(x, pos=None):
     return dates.num2date(x).strftime('%Y-%m-%d') #use FuncFormatter to format dates

x1 = df['day'].tolist()
x = md.datestr2num(x1)
y = df['dtm'].tolist()
z = df['ytm'].tolist()


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_trisurf(x, y, z, cmap=cm.viridis, linewidth=0)
ax.set_zlim(0, .02)

ax.w_xaxis.set_major_locator(MaxNLocator(6)) 
ax.w_xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
ax.yaxis.set_major_locator(MaxNLocator(6))
ax.zaxis.set_major_locator(MaxNLocator(5))
for tl in ax.w_xaxis.get_ticklabels(): # re-create what autofmt_xdate but with w_xaxis
       tl.set_ha('right')
       tl.set_rotation(30)  

fig.colorbar(surf, shrink=0.5, aspect=5)
plt.title('STRIPSs Yield')
fig.tight_layout()


plt.show()