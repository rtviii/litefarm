import json
from pprint import pprint
import matplotlib.pyplot as plt
import os
from numpy import arange
import seaborn as sns

areas = []  #489 farms total
for file in os.listdir('/home/rxz/dev/litefarm/locations'):
    with open("locations/"+file, 'rb') as infile:
        try:
            S =json.load(infile)['total_area']
            areas.append(S)
        except:
            # print("X")
            ...

pprint([* map(lambda k: k/10**4,areas[10:450]) ])
areas.sort()  
sns.displot([* map(lambda k: k/10**4,areas[10:475]) ], bins=20)

plt.ylabel("Number of Farms", fontsize=20)
plt.xlabel("Areas Sum( ha | 0.01 km² )", fontsize=20)
plt.show()