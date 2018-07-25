#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 11:00:38 2018

@author: zrachlin
"""

import spotipy
import spotipy.util as util
import time
from operator import itemgetter
from random import shuffle
import lyricsgenius as genius
from keys import user,genius_token

# Setting authorization scope (see https://developer.spotify.com/documentation/general/guides/scopes/ for more info):
scope = 'playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read user-library-modify user-read-playback-state user-modify-playback-state user-read-currently-playing user-top-read'

#alternative credential option:
#from spotipy.oauth2 import SpotifyClientCredentials
#client_credentials_manager = SpotifyClientCredentials()
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


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
            result = sp.search(q=self.name,type=self.type,limit=1)[self.type+'s']['items'][0]
        return result
    
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
    
    def saveItem(self):
        # Not sure if putting it here is the best place. Other option is in the User object
        sp = getSpotifyCreds(user,scope)
        trackIDs = [self.id] if self.type=='track' else [i.id for i in self.getTracks()]
        alreadySaved = sp.current_user_saved_tracks_contains(tracks=trackIDs) #check if the tracks are already saved
        print('\n'.join("'{}' is already saved".format(Track(ID=i).name) for i,j in zip(trackIDs,alreadySaved) if j))
        newIDs = [i for i,j in zip(trackIDs,alreadySaved) if not j]
        if newIDs:
            sp.current_user_saved_tracks_add(tracks=newIDs)
        
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
        AvgFeatures() -> calculates and prints the average feature values for the artists' top 10 tracks
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
    
    def getTracks(self):
        result = self.getTopTracks()
        print('Using top {} tracks for artist {}'.format(len(result),self.name))
        return result
    
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
        dateStruct() -> converts the album release date to a time object that can be compared with other dates.
        getArtists()
        getArtist() -> the primary artist
    
    Printing Methods:
        Tracks()
        Artists()
        Artist()
        AvgFeatures() -> calculates and prints the average feature values across all of the album's tracks
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
        # Converts the album release date to a time object that can be compared with other dates.
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
        print(self.name,'Tracks:')
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
        
    Printing Methods:
        Artists()
        Artist() -> primary artist
        Album()
    
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
        try:
            features = sp.audio_features(self.id)[0]
        except:
            # API errored out
            features = {}
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
    
    def getLyrics(self):
        genius_api = genius.Genius(genius_token)
        result = genius_api.search_song(self.name,self.artist,verbose=False)
        if not result:
            # This is a simple hack for when Spotify has an extended name for a track that Genius can't find.
            # For example, Track('let it be')'s full name is 'Let It Be - Remastered 2009'. If we remove everything
            # after the hyphen, Genius can find it. This may be risky if the song actually has a hypen in it.
            simpler_name = self.name.split('-')[0].split('(')[0].strip()
            result = genius_api.search_song(simpler_name,self.artist,verbose=False)
            
            # The result is an object with more attributes than just the lyrics. More can be done with this 
            # in the future, like getting the youtube link or links to info about the songwriters.
        return result
    
    def Lyrics(self):
        lyrics = self.getLyrics()
        if lyrics:
            print('Lyrics for {} by {}'.format(self.name,self.artist))
            print('-----------------------------------')
            print(lyrics.lyrics)
        else:
            print('Could not find lyrics')

class Playlist(SpotifyObj):
    '''
    Playlist class for OOSpotify. Inherits functionality from the SpotifyObj Class.
    
    Here are all of the methods (the names should hopefully be sufficiently self-explanatory):
    
    Functional Methods:
        getTracks()
        addTracks()
    
    Printing Methods:
        Tracks()
        AvgFeatures() -> calculates and prints the average feature values across all of the playlist's tracks
    ----------------------------------
    '''
    def __init__(self,name=None,ID=None,playlistDict=None,userID=None,userName=None):
        self.type = 'playlist'
        if not any([name,ID,playlistDict]):
            raise ValueError('You have to enter either the playlist name, the playlist ID, or the playlist dictionary')
        self.name = name
        self.id = ID
        self.playlistDict = playlistDict
        self.userID = userID
        self.userName = userName
        if self.name:
            if self.userID:
                # If you're searching for a popular playlist, it'll be quicker to do a regular search for the first result
                # than to look through every one of the user's playlists for the one that matches, especially if they
                # have a ton of playlists. For example, looking for 'the sound of drum and bass' from user 'thesoundsofspotify'
                first_result = self._getDict()
                if first_result['owner']['id'] == self.userID:
                    self._addAttributes(attDict=first_result)
                else:
                    pl = [i for i in User(self.userID).getPlaylists() if i.name.lower() == self.name.lower()]
                    if pl: 
                        if len(pl)>1:
                            print('Multiple playlists with this name found for this userID, so returning the first result')
                        self._addAttributes(attDict=pl[0].playlistDict)
                    else:
                        print('No playlists with this name were found with this userID')
            elif self.userName:
                # This is a brute force search through all playlists with the same name, trying to match their owner
                # to the provided userName. It will take a ton of time if it's a commonly named playlist. It also 
                # doesn't work very well, so it's better to look up their userID instead.
                # This will have to suffice until this issue gets resolved: https://github.com/spotify/web-api/issues/347
                sp = getSpotifyCreds(user,scope)
                playlists = sp.search(q=self.name,type=self.type,limit=50)['playlists']
                pls = []
                pls += playlists['items']
                while playlists['next']:
                    sp = getSpotifyCreds(user,scope)
                    playlists = sp.next(playlists)['playlists']
                    pls += playlists['items']
                pl = [i for i in pls if i['owner']['display_name'] == self.userName.title()]
                if pl:
                    if len(pl)>1:
                        print('Multiple playlists with this name found for this userName, so returning the first result')
                    self.playlistDict = pl[0]
                    self._addAttributes()
                else:
                    print('Nothing was found')
            else:
                # No userID or userName provided, so just do a normal search and return the first result
                self._addAttributes(attDict=None)
                self.userID = self.owner['id']
                self.userName = self.owner['display_name']
               

        elif self.id:
            if self.userID:
                sp = getSpotifyCreds(user,scope)
                self.playlistDict = sp.user_playlist(self.userID,self.id)
                self._addAttributes(attDict=self.playlistDict)
            else:
                raise ValueError('You need the userID in addition to the playlistID')
        elif self.playlistDict:
            self._addAttributes(attDict=self.playlistDict)
            self.userID = self.owner['id']
            self.userName = self.owner['display_name']
    
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
        
    def addTracks(self,SpotifyObjs,dedup=True):
        if type(SpotifyObjs) is not list:
            SpotifyObjs = [SpotifyObjs]
        listoflists = [[i] if i.type=='track' else i.getTracks() for i in SpotifyObjs]
        trackIDs = [i.id for group in listoflists for i in group]
        if dedup:
            # Remove duplicates
            trackIDs = list(set(trackIDs))
            
        # Split into list of lists with max length = 100 -> the API will only accept 100 at a time.
        maxIDs = 100
        splitTrackIDs = [trackIDs[i:i+maxIDs] for i in range(0,len(trackIDs),maxIDs)]
        for trackIDs in splitTrackIDs:
            sp = getSpotifyCreds(user,scope)
            sp.user_playlist_add_tracks(user=user,playlist_id=self.id,tracks=trackIDs)
 
class User(object):
    '''
    User class for OOSpotify. Allows access to a user's playlists.
    
    Here are all of the methods (the names should hopefully be sufficiently self-explanatory):
    
    Functional Methods:
        getPlaylists()
        getPlaylist(playlistName)
        getSavedTracks() -> only works if you are requesting for yourself
        getTopTracks(limit=50,time_range='medium_term') -> only works if you are requesting for yourself
        getTopArtists(limit=50,time_range='medium_term') -> only works if you are requesting for yourself
        createPlaylist(playlistName) -> only works if you are requesting for yourself
    
    Printing Methods:
        Playlists()
        Playlist(playlistName)
        SavedTracks() -> only works if you are requesting for yourself
        TopTracks(limit=50,time_range='medium_term') -> only works if you are requesting for yourself
        TopArtists(limit=50,time_range='medium_term') -> only works if you are requesting for yourself
        
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
    
    def getPlaylist(self,playlistName):
        pls = [i for i in self.getPlaylists() if i.name.lower() == playlistName.lower()]
        if len(pls) == 1:
            return pls[0]
        else:
            return pls
    
    def Playlist(self,playlistName):
        print('\n'.join('{}. {} -- {}'.format(i,j.name,j.artist) for i,j in enumerate(self.getPlaylist(playlistName).getTracks())))
    
    def getSavedTracks(self):
        #only works if you are requesting your own saved tracks
        if self.id is not user:
            raise ValueError('You can only view your own saved tracks')
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
            
    def SavedTracks(self):
        print('\n'.join('{}. {} -- {}'.format(i,j.name,j.artist) for i,j in enumerate(self.getSavedTracks())))
    
    def getTopTracks(self,limit=50,time_range='medium_term'):
        # From Spotify Web API:
        # time_range = Over what time frame the affinities are computed. 
        # Valid values: 
        # long_term (calculated from several years of data and including all new data as it becomes available), 
        # medium_term (approximately last 6 months)
        # short_term (approximately last 4 weeks)
        # Default: medium_term
        
        if self.id is not user:
            raise ValueError('You can only view your own top tracks')
        sp = getSpotifyCreds(user,scope)
        tracks = sp.current_user_top_tracks(limit=limit,time_range=time_range)['items']
        return [Track(trackDict=i) for i in tracks]
    
    def TopTracks(self,limit=50,time_range='medium_term'):
        print('\n'.join('{}. {} -- {}'.format(i,j.name,j.artist) for i,j in enumerate(self.getTopTracks(limit=limit,time_range=time_range))))
    
    def getTopArtists(self,limit=50,time_range='medium_term'):
        # From Spotify Web API:
        # time_range = Over what time frame the affinities are computed. 
        # Valid values: 
        # long_term (calculated from several years of data and including all new data as it becomes available), 
        # medium_term (approximately last 6 months)
        # short_term (approximately last 4 weeks)
        # Default: medium_term
        if self.id is not user:
            raise ValueError('You can only view your own top artists')
        sp = getSpotifyCreds(user,scope)
        artists = sp.current_user_top_artists(limit=limit,time_range=time_range)['items']
        return [Artist(artistDict=i) for i in artists]
    
    def TopArtists(self,limit=50,time_range='medium_term'):
        print('\n'.join('{}. {}'.format(i,j.name) for i,j in enumerate(self.getTopArtists(limit=limit,time_range=time_range))))
        
    def createPlaylist(self,playlistName,description=None):
        if self.id is not user:
            raise ValueError('You can only create playlists for yourself')
        
        playlists = User(user).getPlaylists()
        dupPlaylists = [p for p in playlists if p.name == playlistName]
        if dupPlaylists:
            ans = input('Playlist with this name already exists. Do you want to overwrite it? (y/n)')
            if ans == 'y':
                sp = getSpotifyCreds(user,scope)
                sp.user_playlist_replace_tracks(user=self.id,playlist_id=dupPlaylists[0].id,tracks=[])
                result = Playlist(playlistDict=dupPlaylists[0].playlistDict)
            else:
                return 'Exiting ...'
        else:
            sp = getSpotifyCreds(user,scope)
            plDict = sp.user_playlist_create(user=self.id,name=playlistName) #creates a new playlist and returns its dict
            result = Playlist(playlistDict=plDict)
        if description:
            sp.user_playlist_change_details(self.id,playlist_id=result.id,description=description)
        return result
    
    def recPlaylist(self,playlistName,recList):
        # Combines creating a playlist and adding tracks and description into one method
        self.createPlaylist(playlistName,description=recList[1]).addTracks(recList[0])
    
    def getPlayingTrack(self):
        sp = getSpotifyCreds(user,scope)
        result = sp.currently_playing()
        if result:
            result = Track(trackDict=result['item'])
        else:
            print('Nothing is currently playing')
        return result
     
    def PlayingTrack(self):
        track = self.getPlayingTrack()
        if track:
            print('{} -- {}'.format(track.name,track.artist))
        
################################################################################################################
# General Functions
            
def getRecs(genres=[],artists=[],tracks=[],SpotifyObjs=[],includeSeedTracks=True,banned_artists=[],banned_tracks=[],
            prompt=False,
                min_acousticness = None,    max_acousticness = None,    target_acousticness = None,
                min_danceability = None,    max_danceability = None,    target_danceability = None,
                 min_duration_ms = None,     max_duration_ms = None,     target_duration_ms = None,
                      min_energy = None,          max_energy = None,          target_energy = None,
            min_instrumentalness = None,max_instrumentalness = None,target_instrumentalness = None,
                         min_key = None,             max_key = None,             target_key = None,
                    min_liveness = None,        max_liveness = None,        target_liveness = None,
                    min_loudness = None,        max_loudness = None,        target_loudness = None,
                        min_mode = None,            max_mode = None,            target_mode = None,
                  min_popularity = None,      max_popularity = None,      target_popularity = None,
                 min_speechiness = None,     max_speechiness = None,     target_speechiness = None,
                       min_tempo = None,           max_tempo = None,           target_tempo = None,
              min_time_signature = None,  max_time_signature = None,  target_time_signature = None,
                     min_valence = None,         max_valence = None,         target_valence = None):
    sp = getSpotifyCreds(user,scope)
    
    if prompt and not all([genres,artists,tracks,SpotifyObjs]): #only allow prompting if no inputs were given
        # To Do: Step-by-step prompts for genres,artists, and track seeds and filters/bans
        pass
    
    genreSeeds = sp.recommendation_genre_seeds()['genres']
    invalids = '\n'.join('{} is an invalid genre'.format(g) for g in genres if g not in genreSeeds)
    if invalids:
        print(invalids)
        print('Genre Options:')
        print(genreSeeds)
        return
    
    seeds = []
    seeds += [(g,'Genres') for g in genres]
    seeds += [(Artist(a),'Artists') for a in artists]
    seeds += [(Track(t),'Tracks') for t in tracks]
    seeds += [(t,'Tracks') for t in extractTracks(SpotifyObjs)]
    
    # The maximum # of seeds you can send to the API for recommendations at one time is 5. We'll split the requested
    # seeds into groups of 5 and then combine the results later, which allows us to take in as many seeds as desired.
    maxSeeds = 5
    splitSeeds = [seeds[i:i+maxSeeds] for i in range(0,len(seeds),maxSeeds)] 
    
    rawRecTrackDicts = []
    
    # Add in Seed Tracks
    if includeSeedTracks:
        rawRecTrackDicts += [Track(t).trackDict for t in tracks]
    
    g = []
    a = []
    t = []
    for seeds in splitSeeds:
        sp = getSpotifyCreds(user,scope)
        Genres = [item[0] for item in seeds if item[1]=='Genres']
        g += Genres
        Artists = [item[0] for item in seeds if item[1]=='Artists']
        a += Artists
        Tracks = [item[0] for item in seeds if item[1]=='Tracks']
        t += Tracks
        recs = sp.recommendations(seed_artists = [a.id for a in Artists],
                                  seed_tracks  = [t.id for t in Tracks],
                                  seed_genres  = [g for g in Genres],limit=100,
                                  min_acousticness = min_acousticness,max_acousticness = max_acousticness,target_acousticness = target_acousticness,
                                  min_danceability = min_danceability,max_danceability = max_danceability,target_danceability = target_danceability,
                                   min_duration_ms = min_duration_ms,max_duration_ms = max_duration_ms,target_duration_ms = target_duration_ms,
                                        min_energy = min_energy,max_energy = max_energy,target_energy = target_energy,
                              min_instrumentalness = min_instrumentalness,max_instrumentalness = max_instrumentalness,target_instrumentalness = target_instrumentalness,
                                           min_key = min_key,max_key = max_key,target_key = target_key,
                                      min_liveness = min_liveness,max_liveness = max_liveness,target_liveness = target_liveness,
                                      min_loudness = min_loudness,max_loudness = max_loudness,target_loudness = target_loudness,
                                          min_mode = min_mode,max_mode = max_mode,target_mode = target_mode,
                                    min_popularity = min_popularity,max_popularity = max_popularity,target_popularity = target_popularity,
                                   min_speechiness = min_speechiness,max_speechiness = max_speechiness,target_speechiness = target_speechiness,
                                         min_tempo = min_tempo,max_tempo = max_tempo,target_tempo = target_tempo,
                                min_time_signature = min_time_signature,max_time_signature = max_time_signature,target_time_signature = target_time_signature,
                                       min_valence = min_valence,max_valence = max_valence,target_valence = target_valence)['tracks']
        rawRecTrackDicts += recs

    # Remove Empty/Unavailable Tracks
    # For some reason, the recommendation engine can give tracks with valid ids that aren't actually available 
    # to play in spotify. They show up as blanks for the track name and artist name.
    rawRecTrackDicts = [i for i in rawRecTrackDicts if i['name'] and i['artists']]
        
    # Remove Duplicates
    # If there are more than 5 requested seeds there may be duplicates because 
    # we are combining multiple sp.recommentations() calls
    recTrackDicts = []
    for track in rawRecTrackDicts:
        if track not in recTrackDicts:
            recTrackDicts.append(track)
            
    # Shuffle
    shuffle(recTrackDicts)
    
    # Create Track Objects:
    recTracks = [Track(trackDict=i) for i in recTrackDicts]
    
    # Remove Banned Artists and Tracks:
    if banned_tracks:
        banned_tracks = [Track(i).name for i in banned_tracks]
        recTracks = [i for i in recTracks if i.name not in banned_tracks]
    if banned_artists:
        banned_artists = [Artist(i).name for i in banned_artists]
        recTracks = [i for i in recTracks if i.artist not in banned_artists]
    
    # Display Playlist
    print('\n'.join('{} -- {}'.format(i.name,i.artist) for i in recTracks))
    
    # Add description of playlist
    description = ''
    if g:
        description += 'Genres: [{}]'.format(', '.join([i.title() for i in g]))
    if a:
        description += ' Artists: [{}]'.format(', '.join([i.name for i in a]))
    if t:
        description += ' Tracks: [{}]'.format(', '.join([i.name for i in t]))
    
    result = [recTracks,description.strip()]
    
    print('\nTotal Tracks: {}'.format(len(recTracks)))
    return result

def orderbyFeatures(SpotifyObjs,features):
    tracks = extractTracks(SpotifyObjs)
    tracks = [t for t in tracks if t.features]
    if type(features) is not list:
        features = [features]
    
    for f in features[::-1]:
        tracks = sorted(tracks,key=lambda x: x.features[f],reverse=True)
    
    for i,t in enumerate(tracks):
        fstring = ', '.join('{}: {}'.format(f,t.features[f]) for f in features)
        print('{}. {} -- {} --> {}'.format(i,t.name,t.artist,fstring))

def extractTracks(SpotifyObjs):
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
                raise ValueError('{} is an invalid object class'.format(obj))
        return trackList
    