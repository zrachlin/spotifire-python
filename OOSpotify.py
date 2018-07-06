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

#alternative credential option:
#from spotipy.oauth2 import SpotifyClientCredentials
#client_credentials_manager = SpotifyClientCredentials()
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

os.environ['SPOTIPY_CLIENT_ID'] = '0dd677ab735f4fd1b9dbf6b236350ba1'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'bbe8736a14ba4e64bfb2d4103c8957aa'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://google.com/'

#UserID:
users = {}
users['zach'] = str(121068889)
users['eva'] = str(126233477)
scope = 'playlist-modify-private playlist-read-private user-library-read user-library-modify'

user = users['zach']

def getSpotifyCreds(user,scope='playlist-modify-private playlist-read-private user-library-read user-library-modify'):
    '''
    Goes through the authorization credential flow for accessing the spotify Web API with the proper permissions (scope). 
    This gets used frequently throughout the SpotifyObj classes in order to refresh the token during each call. This may be
    inefficient, but it seems to be working as a way to prevent errors from token expiration during a long call to the API.
    The alternative is to put long calls within 'try-except' blocks containing the util.prompt_for_user_token() and spotipy.Spotify() calls.
    
    Inputs: 
        user - spotify userID
        scope - permissions -> defaults are user-library-read and user-read-private, which allows access to the current users
        private and public playlists -> see https://developer.spotify.com/documentation/general/guides/scopes/ for more info on scopes
        
    Output:
        spotipy object to be used for making requests to the Spotify Web API
    '''
    token = util.prompt_for_user_token(user,scope)
    return spotipy.Spotify(auth=token)

###############################################################################
# Classes
class SpotifyObj(object):
    '''
    Parent class for the Artist, Album, Track, and Playlist classes used in OOSpotify. 
    Not to be instantiated itself, only used for inheritance.
    '''
    def __init__(self):
        # The first thing that each inheriting class has to do is set the id and type to override these
        self.type = ''
        self.id = ''
    def _getID(self,name):
        sp = getSpotifyCreds(user,scope)
        result = sp.search(q=name,type=self.type,limit=1)
        return result[self.type+'s']['items'][0]['id']
    def _getInfo(self):
        sp = getSpotifyCreds(user,scope)
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
    '''
    Artist class for OOSpotify. Inherits functionality from the SpotifyObj Class.
    
    The methods are split into two types: functional and printing. The former return an object or list of 
    SpotifyObj objects, which can then have their corresponding methods called. The latter are just for viewing 
    purposes and get printed to the console.
    
    For example, if you wanted to see all of alt-J's albums, you'd use the Albums() printing method: 
    Artist('alt-J').Albums(). This prints out a list in descending chronological order of their albums with the 
    respective release dates. If you then wanted to find out the track names for their oldest album,
    you could call the getAlbums() functional method: oldest_album = Artist('alt-J').getAlbums()[-1]. 
    oldest_album is now an object of class Album, which means that you can use the Album methods on it (again, either 
    functional or printing) like so: oldest_album.Tracks(). This prints out all of the track names for the oldest 
    album. Fun stuff!
    
    Here are all of the methods (the names should hopefully be sufficiently self-explanatory):
    
    Functional Methods:
        getTopTracks()
        getRelatedArtists()
        getAlbums()
        getLatestAlbum()
        getAlbumsBefore(year)
        getAlbumsAfter(year)
    
    Printing Methods:
        TopTracks()
        RelatedArtist()
        Albums()
        LatestAlbum()
        AlbumsBefore(year)
        AlbumsAfter(year)
    ----------------------------------
    '''
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
    
    def getTopTracks(self):
        #Returns a list of dictionaries of tracks
        #not implemented: top tracks by a specific country
        sp = getSpotifyCreds(user,scope)
        result = sp.artist_top_tracks(self.id)['tracks']
        return [Track(trackDict=i) for i in result]
    
    def TopTracks(self):
        for i,track in enumerate(self.getTopTracks()):
            print(i,'--',track.name)
    
    def getRelatedArtists(self):
        sp = getSpotifyCreds(user,scope)
        result = sp.artist_related_artists(self.id)['artists']
        return [Artist(artistDict=i) for i in result]
    
    def RelatedArtists(self):
        for artist in self.getRelatedArtists():
            print(artist.name)
    
    def getAlbums(self,desc_order=True):
        sp = getSpotifyCreds(user,scope)
        albums = sp.artist_albums(self.id,limit=50)
        albs = []
        albs += albums['items']
        while albums['next']:
            sp = getSpotifyCreds(user,scope)
            albums = sp.next(albums)
            albs += albums['items']
        
        # There are sometime duplicate albums (like for Kanye's 'Graduation') 
        # They have different Spotify URI values, but everything else is identical
        # list(set(x)) gets rid of some, but not all. Leaving them in for now, but look into in the future...
        result = list(set([Album(albumDict=i) for i in albs if i['album_group'] == 'album']))
        
        #sort by date
        result = sorted(result,key=lambda album: album.dateStruct(),reverse=desc_order)
        return result

    def Albums(self):
        for i,album in enumerate(self.getAlbums()):
            print('{}: {} -- {}'.format(i,album.name,album.release_date))
    
    def getLatestAlbum(self):
        dateTuple = [(i,i.dateStruct()) for i in self.getAlbums()]
        return max(dateTuple,key=itemgetter(1))[0]
    
    def LatestAlbum(self):
        alb = self.getLatestAlbum()
        print('{}: {}'.format(alb.name,alb.release_date))
    
    def getAlbumsBefore(self,year):
        return [i for i in self.getAlbums() if i.dateStruct()<time.strptime(str(year),'%Y')]
    
    def AlbumsBefore(self,year):
        print('\n'.join('{} - {}'.format(i.name,i.release_date) for i in self.getAlbumsBefore(year)))
    
    def getAlbumsAfter(self,year):
        return [i for i in self.getAlbums() if i.dateStruct()>=time.strptime(str(year),'%Y')]
    
    def AlbumsAfter(self,year):
        print('\n'.join('{} - {}'.format(i.name,i.release_date) for i in self.getAlbumsAfter(year)))
    
    def AvgFeatures(self):
        #averages features from top tracks. this could also be from x albums or something else
        return self.getTopTracks()

class Album(SpotifyObj):
    '''
    Album class for OOSpotify. Inherits functionality from the SpotifyObj Class.
    
    Here are all of the methods (the names should hopefully be sufficiently self-explanatory):
    
    Functional Methods:
        getTracks()
        dateStruct()
    
    Printing Methods:
        Tracks()
        AvgFeatures()
    ----------------------------------
    '''
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
        sp = getSpotifyCreds(user,scope)
        tracks = sp.album_tracks(self.id,limit=50)
        trs = []
        trs += tracks['items']
        while tracks['next']:
            sp = getSpotifyCreds(user,scope)
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
    '''
    Track class for OOSpotify. Inherits functionality from the SpotifyObj Class.
    
    Functional Methods:
        getAudioAnalysis()
        getCodestring()
        getEchoprintstring()
        getArtists()
        getArtist()
        getAlbum()
    
    ----------------------------------
    '''
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
        self.features = self._getFeatures()
    
    def _getFeatures(self):
        relevantFeatures = ['acousticness','danceability','energy','instrumentalness','key','liveness','loudness','mode','speechiness','tempo','time_signature','valence']
        sp = getSpotifyCreds(user,scope)
        return {key:val for key,val in sp.audio_features(self.id)[0].items() if key in relevantFeatures}
    
    def getAudioAnalysis(self):
        sp = getSpotifyCreds(user,scope)
        return sp.audio_analysis(self.id)
    
    def getCodestring(self):
        return self.getAudioAnalysis()['track']['codestring']
    
    def getEchoprintstring(self):
        return self.getAudioAnalysis()['track']['echoprintstring']
    
    def getArtists(self):
        return [Artist(ID=i['id']) for i in self.artists]
    
    def getArtist(self):
        #primary artist
        return self.getArtists()[0]
    
    def getAlbum(self):
        return Album(albumDict=self.album)

class Playlist(SpotifyObj):
    '''
    Playlist class for OOSpotify. Inherits functionality from the SpotifyObj Class.
    
    Here are all of the methods (the names should hopefully be sufficiently self-explanatory):
    
    Functional Methods:
        getTracks()
    
    Printing Methods:
        Tracks()
    ----------------------------------
    '''
    def __init__(self,name=None,ID=None,playlistDict=None):
        self.type = 'playlist'
        if playlistDict:
            self._addAttributes(playlistDict)
            self.ownerid = self.owner['id']
    
    def getTracks(self,limit=None):
        sp = getSpotifyCreds(user,scope)
        tracks = sp.user_playlist_tracks(user=self.ownerid,playlist_id=self.id)
        trs = []
        trs += tracks['items']
        while tracks['next']:
            sp = getSpotifyCreds(user,scope)
            tracks = sp.next(tracks)
            trs += tracks['items']
        result = trs
        return [Track(trackDict=i['track']) for i in result]
    
    def Tracks(self):
        for i in self.getTracks():
            print('{}: {}'.format(i.name, i.getArtist().name))
 
class User:
    '''
    User class for OOSpotify. Allows access to a user's playlists.
    
    Here are all of the methods (the names should hopefully be sufficiently self-explanatory):
    
    Functional Methods:
        getPlaylists()
    
    Printing Methods:
        Playlists()
    ----------------------------------
    '''
    def __init__(self,ID=None):
        if ID:
            self.id = ID
        else:
            raise ValueError('You must enter the userid')
    def getPlaylists(self):
        sp = getSpotifyCreds(user,scope)
        playlists = sp.user_playlists(self.id,limit=50)
        pl = []
        pl += playlists['items']
        while playlists['next']:
            sp = getSpotifyCreds(user,scope)
            playlists = sp.next(playlists)
            pl += playlists['items']
        result = pl
        return [Playlist(playlistDict=i) for i in result]
    def Playlists(self):
        for i,playlist in enumerate(self.getPlaylists()):
            print('{}: {}'.format(i,playlist.name))
