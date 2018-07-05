#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 11:00:38 2018

@author: zrachlin
"""

import spotipy
import spotipy.util as util
import os
import time
from operator import itemgetter


#UserID:
users = {}
users['zach'] = str(121068889)

scope = 'user-library-read user-read-private'
token = util.prompt_for_user_token(users['zach'],scope)
sp = spotipy.Spotify(auth=token)


###############################################################################
# Classes
class SpotifyObj(object):
    def __init__(self):
        # The first thing that each inheriting class has to do is set the id and type to override these
        self.type = ''
        self.id = ''
    def _getID(self,name):
        result = sp.search(q=name,type=self.type,limit=1)
        return result[self.type+'s']['items'][0]['id']
    def _getInfo(self):
        method = getattr(sp,self.type)
        return method(self.id)
    def Attributes(self):
        for i in self.__dict__.keys():
            print(i)
    def _getAttributes(self):
        return [i for i in self.__dict__.keys()]
    def _addAttributes(self,attDict=None):
        if attDict:
            for key,val in attDict.items():
                self.__dict__[key] = val
        else:
            for key,val in self._getInfo().items():
                if key is not 'type' and key is not 'id':
                    self.__dict__[key] = val   

class Artist(SpotifyObj):
    def __init__(self,name=None,ID=None,artistDict=None):
        self.type = 'artist'
        if name:
            self.id = self._getID(name)
            self._addAttributes()
        elif ID:
            self.id = ID
            self._addAttributes()
        elif artistDict:
            self._addAttributes(artistDict)
        else:
            raise ValueError('You have to enter either the artist ID, the artist name, or the artist track dictionary')
    #Returns a list of dictionaries of tracks
    def getTopTracks(self):
        #not implemented: country
        result = sp.artist_top_tracks(self.id)['tracks']
        return [Track(trackDict=i) for i in result]
    def TopTracks(self):
        for track in self.getTopTracks():
            print(track.name)
    def getRelatedArtists(self):
        result = sp.artist_related_artists(self.id)['artists']
        return [Artist(artistDict=i) for i in result]
    def RelatedArtists(self):
        for artist in self.getRelatedArtists():
            print(artist.name)
    def getAlbums(self):
        # There are sometime duplicates (like for Kanye) -> not sure why this is
        albums = sp.artist_albums(self.id,limit=50)
        albs = []
        albs += albums['items']
        while albums['next']:
            albums = sp.next(albums)
            albs += albums['items']
        result = albs
        return [Album(albumDict=i) for i in result if i['album_group'] == 'album']
    def Albums(self):
        for i,album in enumerate(self.getAlbums()):
            print('{}: {}'.format(i,album.name))
    def getLatestAlbum(self):
        dateTuple = [(i,i.dateStruct()) for i in self.getAlbums()]
        return max(dateTuple,key=itemgetter(1))[0]
    def LatestAlbum(self):
        alb = self.getLatestAlbum()
        print('{}: {}'.format(alb.name,alb.release_date))
    def getAlbumsBefore(self,year):
        return [i for i in self.getAlbums() if i.dateStruct()<time.strptime(str(year),'%Y')]
    def albumsBefore(self,year):
        print([i.name for i in self.getAlbumsBefore(year)])
    def getAlbumsAfter(self,year):
        return [i for i in self.getAlbums() if i.dateStruct()>time.strptime(str(year),'%Y')]
    def albumsAfter(self,year):
        print([i.name for i in self.getAlbumsAfter(year)])
    def AvgFeatures(self):
        #averages features from top tracks. this could also be from x albums or something else
        return self.getTopTracks()

class Album(SpotifyObj):
    def __init__(self,name=None,ID=None,albumDict=None):
        self.type = 'album'
        if name:
            self.id = self._getID(name)
            self._addAttributes()
        elif ID:
            self.id = ID
            self._addAttributes()
        elif albumDict:
            self._addAttributes(albumDict)
        else:
            raise ValueError('You have to enter either the album ID, the album name, or the album dictionary')
    def dateStruct(self):
        if self.release_date_precision == 'day':
            form = '%Y-%m-%d'
        elif self.release_date_precision == 'month':
            form = '%Y-%m'
        elif self.release_date_precision == 'year':
            form = '%Y'
        else:
            print(self.release_date_precision,'does not have formatting set up yet')
            return
        return time.strptime(self.release_date,form)
    def getTracks(self):
        # Question: should track objects be added as attributes of an album? same for albums of an artist? or is that too expensive?
        tracks = sp.album_tracks(self.id,limit=50)
        trs = []
        trs += tracks['items']
        while tracks['next']:
            tracks = sp.next(tracks)
            trs += tracks['items']
        result = trs
        return [Track(trackDict=i) for i in result]
    def Tracks(self):
        for i,track in enumerate(self.getTracks()):
            print('{}: {}'.format(i,track.name))
    def AvgFeatures(self):
        features = {}
        tracks = self.getTracks()
        for track in tracks:
            for feature,val in track.features.items():
                if feature not in features:
                    features[feature] = 0
                features[feature] += float(val)
        for feature,val in features.items():
            features[feature] /= len(tracks)
        return features
        
class Track(SpotifyObj):
    def __init__(self,name=None,ID=None,trackDict=None):
        self.type = 'track'
        if name:
            self.id = self._getID(name)
            self._addAttributes()
        elif ID:
            self.id = ID
            self._addAttributes()
        elif trackDict:
            self._addAttributes(trackDict)
        else:
            raise ValueError('You have to enter either the trackID, the track name, or the track dictionary')
        self.features = self.getFeatures()
    def getFeatures(self):
        relevantFeatures = ['acousticness','danceability','energy','instrumentalness','key','liveness','loudness','mode','speechiness','tempo','time_signature','valence']
        return {key:val for key,val in sp.audio_features(self.id)[0].items() if key in relevantFeatures}
    def getAudioAnalysis(self):
        return sp.audio_analysis(self.id)
    def codestring(self):
        return self.getAudioAnalysis()['track']['codestring']
    def echoprintstring(self):
        return self.getAudioAnalysis()['track']['echoprintstring']
    def getArtists(self):
        return [Artist(ID=i['id']) for i in self.artists]
    def getArtist(self):
        #primary artist
        return self.getArtists()[0]
    def getAlbum(self):
        return Album(albumDict=self.album)
    
class User:
    def __init__(self,ID=None):
        if ID:
            self.id = ID
        else:
            raise ValueError('You must enter the userid')
    def getPlaylists(self):
        playlists = sp.user_playlists(self.id,limit=50)
        pl = []
        pl += playlists['items']
        while playlists['next']:
            playlists = sp.next(playlists)
            pl += playlists['items']
        result = pl
        return [Playlist(playlistDict=i) for i in result]
    def Playlists(self):
        for i,playlist in enumerate(self.getPlaylists()):
            print('{}: {}'.format(i,playlist.name))
class Playlist(SpotifyObj):
    def __init__(self,name=None,ID=None,playlistDict=None):
        self.type = 'playlist'
        if playlistDict:
            self._addAttributes(playlistDict)
            self.ownerid = self.owner['id']
    def getTracks(self,limit=None):
        tracks = sp.user_playlist_tracks(user=self.ownerid,playlist_id=self.id)
        trs = []
        trs += tracks['items']
        while tracks['next']:
            tracks = sp.next(tracks)
            trs += tracks['items']
        result = trs
        return [Track(trackDict=i['track']) for i in result]
    def Tracks(self):
        for i in self.getTracks():
            print('{}: {}'.format(i.name, i.getArtist().name))
