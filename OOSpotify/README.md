# OOSpotify

OOSpotify is an object-oriented approach to interacting with the Spotify Web API. 
It uses Paul Lamere's spotipy (https://github.com/plamere/spotipy) as its backbone for connecting to the API and has a lot of
similar functionality to some of spotipy's example functions (https://github.com/plamere/spotipy/tree/master/examples), but it builds in the concepts of Artist, Album, Track, Playlist and User objects for more intuitive operations. Each object takes care of the calls to the Spotify Web API for you and deals with all of the parsing of the returned data. This allows for simplified calls with some fun functionality.

Some examples:
```python
from OOSpotify import * 
kanye = Artist('kanye west')
kanye.TopTracks()
```
For some of that #oldkanye ...
```python
kanye.AlbumsBefore(2015)
```
For some of that #newkanye ...
```python
kanye.LatestAlbum()
```
The call above just prints out the latest album but doesn't actually retain the object for the album. To get that object we can do the following ...
```python
ghosts = kanye.getLatestAlbum()
```
We used the getLatestAlbum() method from the kanye object to create an object of class Album. The ghosts object now has all of our album info.
To check out the tracks ...
```python
ghosts.Tracks() #or kanye.getLatestAlbum().Tracks(), or Artist('kanye west').getLatestAlbum().Tracks() --> OOP ftw
```
Again, this call just prints out the tracks from the album, but doesn't retain objects for each track. 

There's plenty more that can be done with OOSpotify. Check out [OOSpotify_Examples](https://github.com/zrachlin/spotifire/tree/master/OOSpotify/OOSpotify_Examples.ipynb) for an in-depth exploration.
