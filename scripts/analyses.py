#!/usr/bin/python3

from cmath import inf
from importlib.metadata import distribution
from json import load
import os
import pickle
from pprint import pprint
import sys
from typing import List
from matplotlib import pyplot as plt
from matplotlib.patches import Patch, Polygon
import numpy as np
from shapely.ops  import unary_union
import seaborn as sns

from farm import Farm, farm_profile

def farm_ids()->List[str]:
    with open("/home/rxz/dev/litefarm/resources/farm_ids.txt",'r', encoding='utf-8') as infile:
        lines = list(map(str.strip,infile.readlines()))
        return lines

def load_all_farms() ->List[ Farm ]:
    agg        = []
    missingids = []

    for id in farm_ids():
        try:
            agg.append(Farm(id, pkl=pklopen(id)))
        except FileNotFoundError:
            print("Missing: ", id)
            missingids.append(id)
    print("Len aggregate : ",len(agg))
    # print("Missing total : ",len(missingids))

    return agg

pklpath = lambda farm_id: '/home/rxz/dev/litefarm/farms/{}.pickle'.format(farm_id)
pklopen = lambda path:  pickle.load(open(pklpath(path),'rb'));

a            = load_all_farms()
nonzero_area = list(filter(lambda f: f.total_area>5,a))

print("nonzero are", len(nonzero_area))


def locations_by_number()->dict:
    d ={}
    for i in load_all_farms():
        for item in i.locations.items():
            if item[0] not in d:
                d[item[0]] =0
            d[item[0]] +=len( item[1] )
    return d

def plot_locations_n_pie():
    sns.set_theme()
    nlocs= locations_by_number()
    y         = np.array([ *nlocs.values() ])
    labels =[]
    for key in nlocs.keys():
        labels.append( "{}: {}".format   ( str( key[0] ).upper() + key[1:],nlocs[key]) )   
    plt.pie(y, 
    labels = labels, 
    # explode = myexplode,
    textprops={'fontsize':14},
    # labeldistance=0.8,
    shadow = True)
    plt.legend(title = "")
    plt.show() 


 
def areas_distribution():
    ...
def user_activity():
    ...
    
