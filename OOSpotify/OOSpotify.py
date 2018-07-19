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
users['zach'] = '121068889'
#users['eva'] = '126233477'
#users['eli'] = '1210409243'
me = users['zach']
scope = 'playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read user-library-modify user-read-playback-state user-modify-playback-state user-read-currently-playing'

user = me

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
        # The first thing that each inheriting class has to do is set the id and type and name to override these
        self.type = ''
        self.id = ''
        self.name = ''
# Not really needed -> the sp.search returns the dictionary anyway, so removing this saves an API call
#    def _getID(self):
#        sp = getSpotifyCreds(user,scope)
#        result = sp.search(q=self.name,type=self.type,limit=1)
#        return result[self.type+'s']['items'][0]['id']
#    
#    def _getInfo(self):
#            sp = getSpotifyCreds(user,scope)
#            apiCall = getattr(sp,self.type) #makes the actual call to the Spotify Web API
#            return apiCall(self.id)
    
    def _getDict(self):
        sp = getSpotifyCreds(user,scope)
        if self.id:
            apiCall = getattr(sp,self.type)
            result = apiCall(self.id)
        else:
            result = sp.search(q=self.name,type=self.type,limit=1)
        return result[self.type+'s']['items'][0]
    
    def Attributes(self):
        for i in self.__dict__.keys():
            print(i)
    
    def _getAttributes(self):
        return [i for i in self.__dict__.keys()]
    
    def _addAttributes(self,attDict=None):
        if not attDict:
            attDict = self._getDict()
            setattr(self,self.type+'Dict',attDict)
        for key,val in attDict.items():
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
        if not any([name,ID,artistDict]):
            raise ValueError('You have to enter either the artist name, the artist ID, or the artist dictionary')
        self.name = name
        self.id = ID
        self.artistDict = artistDict
        self._addAttributes(attDict=artistDict)
        
    
    def getTopTracks(self):
        #Returns a list of dictionaries of tracks
        #not implemented: top tracks by a specific country
        sp = getSpotifyCreds(user,scope)
        result = sp.artist_top_tracks(self.id)['tracks']
        return [Track(trackDict=i) for i in result]
    
    def TopTracks(self):
        print('\n'.join('{}. {}'.format(i,j.name) for i,j in enumerate(self.getTopTracks())))
    
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
        
        result = []
        #courtesy of plamere's spotipy/examples
        unique_names = set()  # skip duplicate albums
        for album in albs:
            name = album['name'].lower()
            if not name in unique_names and album['album_group'] == 'album':  
                unique_names.add(name)
                result.append(Album(albumDict=album))
        
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
        features = {}
        tracks = self.getTopTracks()
        for track in tracks:
            for feature,val in track.features.items():
                if feature not in features:
                    features[feature] = 0
                features[feature] += float(val)
        for feature,val in features.items():
            features[feature] /= len(tracks)
        return features

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
        if not any([name,ID,albumDict]):
            raise ValueError('You have to enter either the album name, the album ID, or the album dictionary')
        self.name = name
        self.id = ID
        self.albumDict = albumDict
        self._addAttributes(attDict=albumDict)
        
        artists = self.artists
        self.artists = [i['name'] for i in artists]
        self.artistsIDs = [i['id'] for i in artists]
        self.artist = self.artists[0]
        self.artistID = self.artistsIDs[0]
    
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
        print('\n'.join('{}. {} -- {}'.format(i,j.name,j.artist) for i,j in enumerate(self.getTracks())))
    
    def getArtists(self):
        return [Artist(ID=i) for i in self.artistsIDs]
    
    def Artists(self):
        print('\n'.join('{}'.format(i) for i in self.artists))
    
    def getArtist(self):
        #primary artist
        return Artist(ID=self.artistID)
    
    def Artist(self):
        print('{}'.format(self.artist))
    
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
        if not any([name,ID,trackDict]):
            raise ValueError('You have to enter either the track name, the track ID, or the track dictionary')
        self.name = name
        self.id = ID
        self.trackDict = trackDict
        self._addAttributes(attDict=trackDict)
        
        self.features = self._getFeatures()
        artists = self.artists
        self.artists = [i['name'] for i in artists]
        self.artistsIDs = [i['id'] for i in artists]
        self.artist = self.artists[0]
        self.artistID = self.artistsIDs[0]
    
    def _getFeatures(self):
        relevantFeatures = ['acousticness','danceability','energy','instrumentalness','key','liveness','loudness','mode','speechiness','tempo','time_signature','valence']
        sp = getSpotifyCreds(user,scope)
        
        features = sp.audio_features(self.id)[0]
        if features:
            return {key:val for key,val in features.items() if key in relevantFeatures}
        else:
            #no features
            return {}
        
    def getAudioAnalysis(self):
        sp = getSpotifyCreds(user,scope)
        return sp.audio_analysis(self.id)
    
    def getCodestring(self):
        return self.getAudioAnalysis()['track']['codestring']
    
    def getEchoprintstring(self):
        return self.getAudioAnalysis()['track']['echoprintstring']
    
    def getArtists(self):
        return [Artist(ID=i) for i in self.artistsIDs]
    
    def Artists(self):
        print('\n'.join('{}'.format(i) for i in self.artists))
    
    def getArtist(self):
        #primary artist
        return Artist(ID=self.artistID)
    
    def Artist(self):
        print('{}'.format(self.artist))
    
    def getAlbum(self):
        return Album(albumDict=self.album)
    
    def Album(self):
        print('{}'.format(self.getAlbum().name))

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
    def __init__(self,name=None,ID=None,playlistDict=None,userID=None,userName=None):
        self.type = 'playlist'
        self.name = name
        self.id = ID
        self.playlistDict = playlistDict
        self.userID = userID
        self.userName = userName
        if self.name:
            if self.userID:
                pl = [i for i in User(self.userID).getPlaylists() if i.name == self.name]
                if pl: 
                    if len(pl)>1:
                        print('Multiple playlists with this name found for this userID, so returning the first result')
                    self._addAttributes(attDict=pl[0].playlistDict)
                else:
                    # No playlists with this name were found with this userID.
                    pass
            elif userName:
                pass
            else:
                # No userID or userName provided, so just do a normal search and return the first result
                self._addAttributes(attDict=None)
               
        
        # waiting for this issue to be resolved: https://github.com/spotify/web-api/issues/347
        
        elif ID:
            self.id = ID
            self._addAttributes()
        elif playlistDict:
            self._addAttributes(playlistDict)
        else:
            raise ValueError('You have to enter either the playlist name, the playlist ID, or the playlist dictionary')
    
    def _getInfo(self):
        sp = getSpotifyCreds(user,scope)
        # This rarely works -> look into this in the future
        if hasattr(self,'ownerID'):
            playlists = User(self.owner).getPlaylists()
            pls = []
            pls += playlists['items']
            while playlists['next']:
                sp = getSpotifyCreds(user,scope)
                playlists = sp.next(playlists)['playlists']
                pls += playlists['items']
            result = [i for i in pls if i['owner']['display_name']==self.owner][0] 
        else:
            result = sp.search(q=self.name,type=self.type,limit=1)[self.type+'s']['items'][0]
        
        return result
    
    def getTracks(self,limit=None):
        sp = getSpotifyCreds(user,scope)
        tracks = sp.user_playlist_tracks(user=self.userID,playlist_id=self.id)
        trs = []
        trs += tracks['items']
        while tracks['next']:
            sp = getSpotifyCreds(user,scope)
            tracks = sp.next(tracks)
            trs += tracks['items']
        result = trs
        return [Track(trackDict=i['track']) for i in result]
    
    def Tracks(self):
        print('\n'.join('{}. {} -- {}'.format(i,j.name,j.artist) for i,j in enumerate(self.getTracks())))
    
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
    
    def _createPlaylist(self):
        playlists = User(user).getPlaylists()
        dupPlaylists = [p for p in playlists if p.name == self.name]
        if dupPlaylists:
            ans = input('Playlist with this name already exists. Do you want to overwrite it? (y/n)')
            if ans == 'y':
                sp = getSpotifyCreds(user,scope)
                sp.user_playlist_replace_tracks(user=user,playlist_id=dupPlaylists[0].id,tracks=[])
                return Playlist(ID=dupPlaylists[0].id)
            else:
                return 'Exiting ...'
        else:
            sp = getSpotifyCreds(user,scope)
            plDict = sp.user_playlist_create(user=user,name=self.name) #creates a new playlist and returns its dict
            return Playlist(playlistDict=plDict)
        
    def addTracks(self,SpotifyObjs):
        trackIDs = self._extractTrackIDs(SpotifyObjs)
        sp = getSpotifyCreds(user,scope)
        sp.user_playlist_add_tracks(user=user,playlist_id=self.id,tracks=trackIDs)
    
    def _extractTrackIDs(self,SpotifyObjs):
        if type(SpotifyObjs) is not list:
            SpotifyObjs = [SpotifyObjs]
        trackList = []
        for obj in SpotifyObjs:
            if obj.type == 'track':
                trackList.append(obj)
            elif obj.type == 'artist':
                tracks = obj.getTopTracks()
                trackList += tracks
                print('Using top {} tracks for artist {}'.format(len(tracks),obj.name))
            elif obj.type in ['playlist','album']:
                tracks = obj.getTracks()
                trackList += tracks
            else:
                #invalid type
                pass
        return [t.id for t in trackList]
 
class User(object):
    '''
    User class for OOSpotify. Allows access to a user's playlists.
    
    Here are all of the methods (the names should hopefully be sufficiently self-explanatory):
    
    Functional Methods:
        getPlaylists()
        getSavedTracks() - only works if you are requesting for yourself
    
    Printing Methods:
        Playlists()
    ----------------------------------
    '''
    def __init__(self,ID=None):
        if ID:
            self.id = ID
            sp = getSpotifyCreds(user,scope)
            self.userDict = sp.user(self.id)
            self.name = self.userDict['display_name']
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
        print('\n'.join('{}: {}'.format(i,j.name) for i,j in enumerate(self.getPlaylists())))
    
    def getSavedTracks(self):
        #only works if you are requesting your own saved tracks
        if self.id == me:
            sp = getSpotifyCreds(user,scope)
            tracks = sp.current_user_saved_tracks(limit=50)
            trs = []
            trs += tracks['items']
            while tracks['next']:
                sp = getSpotifyCreds(user,scope)
                tracks = sp.next(tracks)
                trs += tracks['items']
            result = trs
            return [Track(trackDict=i['track']) for i in result]
        else:
            raise ValueError('You can only view your own saved tracks')
    
    def SavedTracks(self):
        print('\n'.join('{}. {} -- {}'.format(i,j.name,j.artist) for i,j in enumerate(self.getSavedTracks())))
    
    