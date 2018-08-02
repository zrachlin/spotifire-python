#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 13:16:48 2018

@author: zrachlin
"""

from OOSpotify import *
import pandas as pd

def featureComp(SpotifyObjs,features='all',visual='plot'):
    data = []
    if type(SpotifyObjs) is not list:
            SpotifyObjs = [SpotifyObjs]
    featureNames = list(SpotifyObjs[0].features.keys() if SpotifyObjs[0].type == 'track' else SpotifyObjs[0].AvgFeatures().keys())
    for obj in SpotifyObjs:
        if obj.type == 'track':
            features = [val for key,val in obj.features.items()]
            data.append([obj.name,obj.type]+features)
        elif obj.type in ['album','artist','playlist']:
            features = [val for key,val in obj.AvgFeatures().items()]
            data.append([obj.name,obj.type]+features)
        else:
            #invalid type
            pass
    df =  pd.DataFrame(data,columns=['name','type']+featureNames)
    
    ax=df[[i for i in list(df)[2:] if i not in ['key','tempo','loudness','time_signature','Name']]].plot(style='-o',figsize=(10,5))
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.name,rotation=90)
    ax.legend(bbox_to_anchor=(1.05,1))
    return df
#
#import matplotlib.pyplot as plt
#import pandas as pd
#from math import pi
# 
## Set data
#df = pd.DataFrame({
#'group': ['A','B','C','D'],
#'var1': [38, 1.5, 30, 4],
#'var2': [29, 10, 9, 34],
#'var3': [8, 39, 23, 24],
#'var4': [7, 31, 33, 14],
#'var5': [28, 15, 32, 14]
#})
# 
## ------- PART 1: Define a function that do a plot for one line of the dataset!
# 
#def make_spider( row, title, color):
# 
#    # number of variable
#    categories=list(df)[1:]
#    N = len(categories)
#     
#    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
#    angles = [n / float(N) * 2 * pi for n in range(N)]
#    angles += angles[:1]
#     
#    # Initialise the spider plot
#    ax = plt.subplot(2,2,row+1, polar=True, )
#     
#    # If you want the first axis to be on top:
#    ax.set_theta_offset(pi / 2)
#    ax.set_theta_direction(-1)
#     
#    # Draw one axe per variable + add labels labels yet
#    plt.xticks(angles[:-1], categories, color='grey', size=8)
#     
#    # Draw ylabels
#    ax.set_rlabel_position(0)
#    plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
#    plt.ylim(0,40)
#     
#    # Ind1
#    values=df.loc[row].drop('group').values.flatten().tolist()
#    values += values[:1]
#    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
#    ax.fill(angles, values, color=color, alpha=0.4)
#     
#    # Add a title
#    plt.title(title, size=11, color=color, y=1.1)
#     
#    # ------- PART 2: Apply to all individuals
#    # initialize the figure
#    my_dpi=96
#    plt.figure(figsize=(1000/my_dpi, 1000/my_dpi), dpi=my_dpi)
#     
#    # Create a color palette:
#my_palette = plt.cm.get_cmap("Set2", len(df.index))
#     
## Loop to plot
#for row in range(0, len(df.index)):
#    make_spider( row=row, title='group '+df['group'][row], color=my_palette(row))