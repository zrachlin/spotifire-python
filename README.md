# :fire: spotifire :fire:
This project enables interaction with the Spotify Web API (https://developer.spotify.com/documentation/web-api/) through the use of Paul Lamere's spotipy library (https://github.com/plamere/spotipy).

In order to enable some of the Web API functionality, you'll need to register an App through the Spotify Developers Console. It's pretty simple; here are the steps:
1. Go to https://developer.spotify.com/dashboard/
2. Log in to the dashboard with your spotify credentials
3. Click the "CREATE A CLIENT ID" button
4. Give your App whatever name and description you'd like
5. Select "I don't know" in response to "What are you building?" - this will avoid having to deal with questions about commercializing your app
6. Click "NEXT"
7. Accept all of the conditions and click "SUBMIT". You'll be brought to a new page for your newly created App.
8. Click on the "Edit Settings" button
9. Under "Redirect URIs", enter http://google.com/
10. Click "SAVE"
11. Click the "SHOW CLIENT SECRET" button. Copy the Client ID and Client Secret.
12. In OOSpotify.py, enter the following 

os.environ['SPOTIPY_CLIENT_ID'] = 'your client id'

os.environ['SPOTIPY_CLIENT_SECRET'] = 'your client secret'

os.environ['SPOTIPY_REDIRECT_URI'] = 'http://google.com/'

OOSpotify enables you to create objects for albums, artists, tracks, users, and playlists. Each object takes care of the calls to the Spotify Web API for you and deals with all of the parsing of the returned data. This allows for simplified calls with some fun functionality.

Some examples:
```python
from OOSpotify import * 
kanye = Artist('kanye west')
kanye.TopTracks()
```
Returns:
```
0 -- All Mine
1 -- Yikes
2 -- Ghost Town
3 -- Violent Crimes
4 -- Wouldn't Leave
5 -- I Thought About Killing You
6 -- No Mistakes
7 -- Lift Yourself
8 -- Stronger
9 -- FourFiveSeconds
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

ghosts = kanye.getLatestAlbum()

We used the getLatestAlbum() method from the kanye object to create an object of class Album. The ghosts object now has all of our album info.
To check out the tracks ...

ghosts.Tracks() (or kanye.getLatestAlbum().Tracks(), or Artist('kanye west').getLatestAlbum().Tracks() --> OOP ftw)

Again, this call just prints out the tracks from the album, but doesn't retain objects for each track. 

There's plenty more that can be done with OOSpotify. Check out OOSpotify_Examples for an in-depth exploration.

