#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 22:40:58 2018

@author: zrachlin
"""
import logging
from flask import Flask
from flask_ask import Ask, statement, question, session, delegate, request, elicit_slot

import sys
sys.path.append('../OOSpotify/')
from OOSpotify import User,Album,Artist,Track,Playlist, getRecs, availableGenreSeeds
from keys import user
import re

u = User(user)

#import json
#import requests
#import time
#import unidecode

app = Flask(__name__) #app definition for Flask
ask = Ask(app,"/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

def get_dialog_state():
    return session['dialogState']

@ask.launch
def start_skill():
    welcome_message = 'Welcome to Spotifire. What can I help you with?'
    return question(welcome_message)

@ask.intent('saveTrackIntent')
def saveTrack():
    track = u.getPlayingTrack()
    if track:
        message = track.saveItem()
        #The message will be either "Saved it to your music", or "You've already saved this"
    else:
        message = 'Nothing is currently playing' 
    return statement(message)

@ask.intent('createPlaylistIntent',default={'s_one':'','s_two':'','s_three':'',
                                            'g_one':'','g_two':'','g_three':'','g_four':'','g_five':'',
                                            'a_one':'','a_two':'','a_three':'','a_four':'','a_five':'',
                                            't_one':'','t_two':'','t_three':'','t_four':'','t_five':''})
def createPlaylist(s_one,s_two,s_three,playlistName):
    if not any([s_one,s_two,s_three]):
        message = 'What would you like in your playlist?'
    else:
        if s_one:
            s_one = str(request.intent.slots.s_one.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['name'])
        if s_two:
            s_two = str(request.intent.slots.s_two.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['name'])
        if s_three:
            s_three = str(request.intent.slots.s_three.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['name'])
        seeds = [i for i in [s_one,s_two,s_three] if i]

        if 'genres' in seeds and not request.intent.slots.g_one.value:
            return elicit_slot('g_one','Which genres would you like to use as seeds?')
        genreSeeds = availableGenreSeeds()
        genres = []
        for key in ['g_one','g_two','g_three','g_four','g_five']:
            slot = request.intent.slots[key]
            if 'value' in slot:
                genre = slot['value']
                if genre not in genreSeeds:
                    return elicit_slot(key,'{} is an invalid Genre. Please choose a valid genre from the card in the Alexa App.'.format(genre))
#        genres = [request.intent.slots[key]['value'] for key in ['g_one','g_two','g_three','g_four','g_five'] if 'value' in request.intent.slots[key]]
#        genreSeeds = availableGenreSeeds()
#        invalids = '\n'.join('{} is an invalid genre. '.format(g) for g in genres if g not in genreSeeds)
#        if invalids:
#            return elicit_slot('g_one',invalids+'Please choose valid genres.')
            
        if 'artists' in seeds and not request.intent.slots.a_one.value:
            return elicit_slot('a_one','Which artists would you like to use as seeds?')
        
        if 'tracks' in seeds and not request.intent.slots.t_one.value:
            return elicit_slot('t_one','Which tracks would you like to use as seeds?')
        
        slots = request.intent.slots
        genres = [slots[key]['value'] for key in ['g_one','g_two','g_three','g_four','g_five'] if 'value' in slots[key]]
        artists = [slots[key]['value'] for key in ['a_one','a_two','a_three','a_four','a_five'] if 'value' in slots[key]]
        tracks = [slots[key]['value'] for key in ['t_one','t_two','t_three','t_four','t_five'] if 'value' in slots[key]]
        #message = 'i heard {},{},{}'.format(genres,artists,tracks)
        #message = '{},{},{}'.format(request.intent.slots.genres['value'],request.intent.slots.artists['value'],request.intent.slots.tracks['value'])
        
        if not request.intent.slots.playlistName.value:
            return elicit_slot('playlistName','What would you like to name your playlist?')
        recs = getRecs(genres=genres,artists=artists,tracks=tracks)
        pl = u.recPlaylist(playlistName,recs)
        echo_devID = [i['id'] for i in u.getDevices() if i['name'] == "Zach's Echo Dot"][0]
        pl.startPlayback(echo_devID)
        
    return statement('made your playlist: {},{},{}'.format(genres,artists,tracks))

@ask.intent('getSeedsIntent')
def getSeeds():
    session.attributes['cat'] = 'cat'
    #seeds = session.attributes.pop('seeds',None)
    session.attributes['dog'] = 3
    seeds = session.attributes.pop('dog',None)
    if seeds:
        message = 'i founds some seeds ... {}, this is left ... {}'.format(seeds,session.attributes.pop('cat'))
    else:
        message = 'i did not find any seeds'
    return message


@ask.intent('topTracksIntent',default={'limit':5,'time_range':'medium_term'},convert={'limit': int})
def topTracks(limit,time_range):
    time_range = str(request.intent.slots.time_range.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['name'])
    tracks = u.getTopTracks(limit=limit,time_range=time_range)
    if time_range == 'short_term':
        time_msg = 'for the last few weeks'
    elif time_range == 'medium_term':
        time_msg = 'for the last few months'
    elif time_range == 'long_term':
        time_msg = 'of all time'
    else:
        time_msg = ''
    message = 'Your top {} tracks {} are '.format(limit,time_msg) + ', '.join('{} by {}'.format(i.name,i.artist) for i in tracks[:-1]) + ', and {} by {}'.format(tracks[-1].name,tracks[-1].artist)
    return statement(message)

@ask.intent('topArtistsIntent',default={'limit':5,'time_range':'medium_term'},convert={'limit':int})
def topArtists(limit,time_range):
    time_range = str(request.intent.slots.time_range.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['name'])
    artists = u.getTopArtists(limit=limit,time_range=time_range)
    if time_range == 'short_term':
        time_msg = 'for the last few weeks'
    elif time_range == 'medium_term':
        time_msg = 'for the last few months'
    elif time_range == 'long_term':
        time_msg = 'of all time'
    else:
        time_msg = ''
    
    message = 'Your top {} artists {} are '.format(limit,time_msg) + ', '.join('{}'.format(i.name) for i in artists[:-1]) + ', and {}'.format(artists[-1].name)
    return statement(message)

if __name__ == '__main__':
    app.run(debug=True)