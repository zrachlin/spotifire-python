# spotifire
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
11. Click the "SHOW CLIENT SECRET" button
12. In OOSpotify.py, enter the following 

os.environ['SPOTIPY_CLIENT_ID'] = 'your client id'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'your client secret'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://google.com/'

OOSpotify enables you to create objects for albums, artists, tracks, users, and playlists. Each object takes care of the calls to the Spotify Web API for you and deals with all of the parsing of the returned data. This allows for simplified calls with some fun functionality.

Some examples:

kanye = Artist('kanye west')

kanye.TopTracks()

For some of that #oldkanye ...

kanye.AlbumsBefore(2015)

For some of that #newkanye ...

kanye.LatestAlbum()

The call above just prints out the latest album but doesn't actually retain the object for the album. To get that object we can do the following ...

ghosts = kanye.getLatestAlbum()

We used the getLatestAlbum() method from the kanye object to create an object of class Album. The ghosts object now has all of our album info.
To check out the tracks ...

ghosts.Tracks() (or kanye.getLatestAlbum().Tracks(), or Artist('kanye west').getLatestAlbum().Tracks() --> oop ftw)

Again, this call just prints out the tracks from the album, but doesn't retain objects for each track. 

