# :fire: Spotifire :fire:
This project enables musical exploration, playlist creation, and deep learning via interaction with the [Spotify Web API](https://developer.spotify.com/documentation/web-api/) through the use of Paul Lamere's [Spotipy](https://github.com/plamere/spotipy).

The core of Spotifire is called OOSpotify. OOSpotify enables you to create objects for albums, artists, tracks, users, and playlists. Each object takes care of the calls to the Spotify Web API for you and deals with all of the parsing of the returned data. This allows for simplified calls with some fun functionality.

Some examples:
```python
import sys
sys.path.append('../OOSpotify/')
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


## Setup 
### 1: Installation/Dependencies
* Clone this repository -> `git clone https://github.com/zrachlin/spotifire.git`
* Install [Spotipy](https://github.com/plamere/spotipy), courtesy of Paul Lamere -> `git clone https://github.com/plamere/spotipy.git` and install from source with `python setup.py install` (There are some API calls that haven't been included in the pip version yet)
* Install [LyricsGenius](https://github.com/johnwmillr/LyricsGenius), courtesy of johnwmillr -> `pip install lyricsgenius`

For [OOSpotify](https://github.com/zrachlin/spotifire/tree/master/OOSpotify), the following packages are needed. Using Anaconda (https://www.anaconda.com/download) should provide you with everything:
* numpy
* pandas
* matplotlib
* jupyter

For [Genre Prediction using Deep Learning](https://github.com/zrachlin/spotifire/tree/master/Genre_Prediction), the following are needed:
* scipy
* scikit-learn
* tensorflow (and tensorflow-gpu if you want to train on GPUs)
* keras (and keras-gpu version >= 2.0.9 if you want to train on multiple GPUs)

### 2: App Registration
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

### 3. Credentials
Create a file named keys.py in the OOSpotify folder (`spotifire/OOSpotify/keys.py`) and paste in the following code and replace 'your client id' and 'your client secret' with your actual credentials from above:

```python
import os
os.environ['SPOTIPY_CLIENT_ID'] = 'Your Client ID'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'Your Client Secret'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://google.com/'
user = 'Your Spotify User ID'
```
If you don't know your Spotify User ID, here's how to find it using the mobile app:
1. Go to "Your Library" and tap your profile picture in the upper left corner

<img src="https://github.com/zrachlin/spotifire/blob/master/images/Screenshot_20180722-121942_Spotify.jpg" alt="" width="275" height="550"> 

2. Tap the "..." in the upper right corner 

<img src="https://github.com/zrachlin/spotifire/blob/master/images/Screenshot_20180722-121955_Spotify.jpg" alt="" width="275" height="550"> 

3. Tap "Share" and copy the link to your clipboard 

<img src="https://github.com/zrachlin/spotifire/blob/master/images/Screenshot_20180722-122018_Spotify.jpg" alt="" width="275" height="550"> 

4. Paste the link somewhere you can read it. Your User ID is what comes afer `user/` and before the question mark. It can be a string of numbers or text 

<img src="https://github.com/zrachlin/spotifire/blob/master/images/Screenshot_20180722-122055_Samsung%20Notes.jpg" alt="" width="300" height="150">

If you would like to be able to search for track lyrics, you'll need to set up a Genius API Client and get the access token. You can do that [here](https://genius.com/api-clients). Once you've done that, copy the access token and enter it into your keys.py file like so:
```python
genius_token = 'Your Genius Client Access Token'
```
