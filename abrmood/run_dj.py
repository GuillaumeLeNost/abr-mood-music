
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import keyboard
import random
import json
from pprint import pprint

SPOTIPY_CLIENT_ID='869dafb8a8b64759a0886ebc473ee6cb'
SPOTIPY_CLIENT_SECRET='12b5f9739bd247e6bfedf76dfe55393f'
SPOTIPY_REDIRECT_URI='https://www.getpostman.com/oauth2/callback'

def openJson(json_file):
    with open(json_file) as f:
        data = json.load(f)
    return(data)

def getRecommendations(**kwargs):

    recom_tracks = sp.recommendations(limit=100, **kwargs)['tracks']
    result=[]
    for track in recom_tracks:
        result.append(track['id'])
    return result

def getAudioFeatures(track_ids):
    audio_features=sp.audio_features(tracks=track_ids)
    return audio_features

def playSong(uri, token):
    url='https://api.spotify.com/v1/me/player/play'
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+token}
    data='{\"uris\":["'+uri+'"]}'
    response=requests.put(url, data, headers=headers)

def getRecommendationsFromMood(mood):
    mood = "party"
    data = openJson("lookup.json")
    recommendations=getRecommendations(**data[mood])
    audio_features = getAudioFeatures(recommendations)
    return(audio_features)

def run_dj(audio_features):
    active = True
    while active:#making a loop
        # GET EMOTION AND MOOD
        try: #used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed(' '):
                next_audio = audio_features[random.randint(0,len(audio_features ))]['uri']
                playSong(next_audio, user_token)
            elif keyboard.is_pressed('q'):
                active = False
                break
            else:
                pass
        except:
            break


if __name__ == '__main__':

    # ATTENTION! MAKE SURE THE user_token IS WORKING: https://developer.spotify.com/console/get-available-genre-seeds/
    client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
    user_token='BQBNPlsViubqVovIPbD9giKf7WUtFPXolQPo-ZgRN7uw8XV3VQ2RBbvhEC-FlaMjYRRCKfun3jZIO0155hnj58BsqQI1YpPjXB_FUqaGgjxdmdw0Ne20C2Lu9N5_XgpX3XmuHYDrzEJ4nkUPf0Z8QhKYuUSk6p8lafHJB2zL0E5DXqYbIdPA4EQQ0DVaFrilBdpAqFBpYBXwOruZ0vPGsj1aR-77IUPamJImVgPSuiyy6jMbVyNNniuLkFo8JbpuiA2kD2qNJBIkhJ3u6P0'
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, auth=user_token)

    # TO DO:
    audio_features = getRecommendationsFromMood('party')
    run_dj(audio_features)
