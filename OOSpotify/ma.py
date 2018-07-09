#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 13:16:48 2018

@author: zrachlin
"""

from OOSpotify import *
import pandas as pd

def featureComp(SpotifyObjs,features='all',visual='plot'):
    features = []
    names = []
    for obj in SpotifyObjs:
        if obj.type == 'track':
            features.append(obj.features)
            names.append(obj.name)
        elif obj.type in ['album','artist','playlist']:
            features.append(obj.AvgFeatures())
            names.append(obj.name)
        else:
            #invalid type
            pass
    df =  pd.DataFrame(features,index=names).transpose()
    return df